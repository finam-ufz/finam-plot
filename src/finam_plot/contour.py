"""Components for contour plots"""
from datetime import datetime

import finam as fm
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.tri import Triangulation


class ContourPlot(fm.Component):
    """Contour plot component for structured and unstructured grids

    Data must be of grid and FINAM grid type.

    Parameters
    ----------
    limits : tuple of (float, float), optional
        Limits of the colormap limits. Default dynamic.
    axes : (int, int) or (str, str)
        Tuple of axes indices or names.
    fill : bool
        Whether to draw filled contours.
    triangulate : bool
        Allow/force triangulation.
    """

    def __init__(self, limits=(None, None), axes=(0, 1), fill=True, triangulate=False):
        super().__init__()
        self._time = None
        self._figure = None
        self._plot_ax = None
        self._axes = axes
        self._triangulate = triangulate
        self._fill = fill
        self._info = None
        self._contours = None
        self.triangulation = None
        self.vmin = limits[0]
        self.vmax = limits[1]

    def _initialize(self):
        self.inputs.add(
            io=fm.CallbackInput(
                name="Grid",
                callback=self._data_changed,
                time=None,
                grid=None,
                units=None,
            )
        )
        self.create_connector()

    def _connect(self):
        self.try_connect()

        in_info = self.connector.in_infos["Grid"]
        if in_info is not None:
            self._info = in_info

    def _validate(self):
        pass

    def _update(self):
        self._plot()

    def _finalize(self):
        pass

    def _plot(self):
        try:
            data = fm.data.get_magnitude(
                fm.data.strip_time(self._inputs["Grid"].pull_data(self._time))
            )
        except fm.FinamNoDataError as e:
            if self.status in (
                fm.ComponentStatus.VALIDATED,
                fm.ComponentStatus.INITIALIZED,
            ):
                return

            with fm.tools.ErrorLogger(self.logger):
                raise e

        if self._figure is None:
            self._figure, self._plot_ax = plt.subplots()
            self._plot_ax.set_aspect("equal")

        if self._contours is not None:
            self._plot_ax.clear()

        axes_names = {name: i for i, name in enumerate(self._info.grid.axes_names)}
        axes_indices = [
            ax if isinstance(ax, int) else axes_names[ax] for ax in list(self._axes)
        ]

        ax_1 = axes_indices[0]
        ax_2 = axes_indices[1]

        if isinstance(self._info.grid, fm.UnstructuredGrid):
            self._plot_unstructured(data, (ax_1, ax_2))
        else:
            self._plot_structured(data, (ax_1, ax_2))

        self._figure.show()
        self._figure.tight_layout()

        self._figure.canvas.draw()
        self._figure.canvas.flush_events()

    def _plot_structured(self, data, axes):
        if axes == (0, 1):
            if self._info.grid.order == "F":
                data = data.transpose()
        elif axes == (1, 0):
            if self._info.grid.order == "C":
                data = data.transpose()
        else:
            raise ValueError(f"Unsupported axes: {axes}")

        data_axes = [self._info.grid.data_axes[i] for i in axes]

        if self._fill:
            self._contours = self._plot_ax.contourf(
                *data_axes, data, vmin=self.vmin, vmax=self.vmax
            )
        else:
            self._contours = self._plot_ax.contour(
                *data_axes, data, vmin=self.vmin, vmax=self.vmax
            )

    def _plot_unstructured(self, data, axes):
        if self._info.grid.data_location == fm.Location.POINTS:
            needs_triangulation = isinstance(
                self._info.grid, fm.UnstructuredPoints
            ) or any(tp != fm.CellType.TRI.value for tp in self._info.grid.cell_types)

            if needs_triangulation and not self._triangulate:
                with fm.tools.ErrorLogger(self.logger):
                    raise ValueError(
                        "Data requires triangulation. Use with `triangulate=True`"
                    )

            if self.triangulation is None:
                if self._triangulate:
                    self.triangulation = [
                        Triangulation(*self._info.grid.data_points.T[list(axes)])
                    ]
                else:
                    self.triangulation = [
                        *self._info.grid.data_points.T[list(axes)],
                        self._info.grid.cells,
                    ]

            data_flat = np.ascontiguousarray(
                data.reshape(-1, order=self._info.grid.order)
            )
            if self._fill:
                self._contours = self._plot_ax.tricontourf(
                    *self.triangulation, data_flat, vmin=self.vmin, vmax=self.vmax
                )
            else:
                self._contours = self._plot_ax.tricontour(
                    *self.triangulation, data_flat, vmin=self.vmin, vmax=self.vmax
                )
        else:
            if self._fill:
                tris_only = all(
                    tp == fm.CellType.TRI.value for tp in self._info.grid.cell_types
                )

                if not tris_only:
                    with fm.tools.ErrorLogger(self.logger):
                        raise NotImplementedError(
                            "Contour plots for cell data are only supported for triangular meshes"
                        )

                data_flat = np.ascontiguousarray(
                    data.reshape(-1, order=self._info.grid.order)
                )

                self._contours = self._plot_ax.tripcolor(
                    *self._info.grid.points.T[list(axes)],
                    data_flat,
                    triangles=self._info.grid.cells,
                    vmin=self.vmin,
                    vmax=self.vmax,
                )
            else:
                if self.triangulation is None:
                    self.triangulation = [
                        Triangulation(*self._info.grid.data_points.T[list(axes)])
                    ]

                data_flat = np.ascontiguousarray(
                    data.reshape(-1, order=self._info.grid.order)
                )
                self._contours = self._plot_ax.tricontour(
                    *self.triangulation, data_flat, vmin=self.vmin, vmax=self.vmax
                )

    def _data_changed(self, _caller, time):
        if not isinstance(time, datetime):
            with fm.tools.ErrorLogger(self.logger):
                raise ValueError("Time must be of type datetime")

        self._time = time
        if self.status in (fm.ComponentStatus.UPDATED, fm.ComponentStatus.VALIDATED):
            self._update()
        else:
            self._plot()
