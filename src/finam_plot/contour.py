"""Components for contour plots"""
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
from finam.core.interfaces import ComponentStatus, FinamNoDataError
from finam.core.sdk import AComponent, CallbackInput
from finam.data import Info, UnstructuredGrid
from finam.data.grid_spec import CellType, Location, UnstructuredPoints
from finam.tools.connect_helper import ConnectHelper
from finam.tools.log_helper import LogError
from matplotlib.tri import Triangulation


class ContourPlot(AComponent):
    """Plots contours"""

    def __init__(self, axes=(0, 1), fill=True, triangulate=False):
        super().__init__()
        self._time = None
        self._figure = None
        self._axes = axes
        self._triangulate = triangulate
        self._fill = fill
        self._info = None

        self._connector: ConnectHelper = None

        self.status = ComponentStatus.CREATED

    def initialize(self):
        super().initialize()

        self.inputs["Grid"] = CallbackInput(self._data_changed)
        self._connector = ConnectHelper(self.inputs, self.outputs)

        self.status = ComponentStatus.INITIALIZED

    def connect(self):
        super().connect()

        exchange_infos = {"Grid": Info(grid=None, meta={"units": None})}
        self.status = self._connector.connect(None, exchange_infos=exchange_infos)

        in_info = self._connector.in_infos["Grid"]
        if in_info is not None:
            self._info = in_info

    def validate(self):
        super().validate()

        self.status = ComponentStatus.VALIDATED

    def update(self):
        super().update()

        self._plot()

        self.status = ComponentStatus.UPDATED

    def finalize(self):
        super().finalize()

        self.status = ComponentStatus.FINALIZED

    def _plot(self):
        try:
            data = self._inputs["Grid"].pull_data(self._time)
        except FinamNoDataError as e:
            if (
                self.status == ComponentStatus.VALIDATED
                or self.status == ComponentStatus.INITIALIZED
            ):
                return
            else:
                with LogError(self.logger):
                    raise e

        if self._figure is None:
            self._figure, axes = plt.subplots()
            axes.set_aspect("equal")

            axes_names = {name: i for i, name in enumerate(self._info.grid.axes_names)}
            axes_indices = [
                ax if isinstance(ax, int) else axes_names[ax] for ax in list(self._axes)
            ]

            ax_1 = axes_indices[0]
            ax_2 = axes_indices[1]

            if isinstance(self._info.grid, UnstructuredGrid):
                if self._info.grid.data_location == Location.POINTS:
                    needs_triangulation = isinstance(
                        self._info.grid, UnstructuredPoints
                    ) or any(
                        tp != CellType.TRI.value for tp in self._info.grid.cell_types
                    )

                    if needs_triangulation and not self._triangulate:
                        with LogError(self.logger):
                            raise ValueError(
                                "Data requires triangulation. Use with `triangulate=True`"
                            )

                    if self._triangulate:
                        tris = [
                            Triangulation(*self._info.grid.data_points.T[[ax_1, ax_2]])
                        ]
                    else:
                        tris = [
                            *self._info.grid.data_points.T[[ax_1, ax_2]],
                            self._info.grid.cells,
                        ]

                    data_flat = np.ascontiguousarray(
                        data.pint.magnitude.reshape(-1, order=self._info.grid.order)
                    )
                    if self._fill:
                        axes.tricontourf(*tris, data_flat)
                    else:
                        axes.tricontour(*tris, data_flat)
                else:
                    with LogError(self.logger):
                        raise NotImplementedError(
                            "Contour plots are not implemented for cell data"
                        )
            else:
                with LogError(self.logger):
                    raise NotImplementedError(
                        "Contour plots are not implemented for regular grids"
                    )

            self._figure.show()
            self._figure.tight_layout()
        else:
            pass

        self._figure.canvas.draw()
        self._figure.canvas.flush_events()

    def _data_changed(self, _caller, time):
        if not isinstance(time, datetime):
            with LogError(self.logger):
                raise ValueError("Time must be of type datetime")

        self._time = time
        if self.status in (ComponentStatus.UPDATED, ComponentStatus.VALIDATED):
            self.update()
        else:
            self._plot()
