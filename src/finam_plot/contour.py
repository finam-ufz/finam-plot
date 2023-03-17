"""Components for contour plots"""
from datetime import datetime

import finam as fm
import numpy as np
from matplotlib.tri import Triangulation

from .plot import PlotBase
from .tools import create_colorbar


class ContourPlot(PlotBase):
    """Contour plot component for structured and unstructured grids

    Data must be of grid and FINAM grid type.

    Used plot function depends on grid type and fill argument:

    * Structured grids: :func:`matplotlib.pyplot.contour` and :func:`matplotlib.pyplot.contourf`
    * Point data and unstructured grids with point-associated data:
      :func:`matplotlib.pyplot.tricontour` and :func:`matplotlib.pyplot.tricontourf`
    * Unstructured cell data:

      * Filled: :func:`matplotlib.pyplot.tripcolor`
      * Not filled: :func:`matplotlib.pyplot.tricontour`

    Unstructured cell data with quads is currently not supported with ``fill=True``.

    .. code-block:: text

                   +-------------+
                   |             |
        --> [Grid] | ContourPlot |
                   |             |
                   +-------------+

    Note:
        This component is push-based without an internal time step.

    Examples
    --------

    .. testcode:: constructor

        import finam_plot as fmp

        plot = fmp.ContourPlot(
            fill=False,
            triangulate=True,
            vmin=0, vmax=1, cmap="hsv", # plot kwargs
        )

    .. testcode:: constructor
        :hide:

        plot.initialize()

    Parameters
    ----------
    title : str, optional
        Title for plot and window.
    fill : bool, optional
        Whether to draw filled contours. Default ``True``.
    triangulate : bool, optional
        Allow/force triangulation. Default ``False``.
    pos : tuple(number, number), optional
        Figure position. ``int`` is interpreted as pixels,
        ``float`` is interpreted as fraction of screen size.
    size : tuple(number, number), optional
        Figure size. ``int`` is interpreted as pixels,
        ``float`` is interpreted as fraction of screen size.
    update_interval : int, optional
         Redraw interval, in number of push steps.
    **plot_kwargs
        Keyword arguments passed to plot function. See the list of functions above.
    """

    def __init__(
        self,
        title=None,
        fill=True,
        triangulate=False,
        pos=None,
        size=None,
        update_interval=1,
        **plot_kwargs,
    ):
        super().__init__(title, pos, size, update_interval, **plot_kwargs)
        self._time = None
        self._triangulate = triangulate
        self._fill = fill
        self._info = None
        self._contours = None
        self._time_text = None
        self.triangulation = None

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

    def _connect(self, start_time):
        self.try_connect(start_time)

        in_info = self.connector.in_infos["Grid"]
        if in_info is not None:
            self._info = in_info

    def _plot(self):
        try:
            data = fm.data.get_magnitude(self.inputs["Grid"].pull_data(self._time))[
                0, ...
            ]
        except fm.FinamNoDataError as e:
            if self.status in (
                fm.ComponentStatus.VALIDATED,
                fm.ComponentStatus.INITIALIZED,
            ):
                return

            with fm.tools.ErrorLogger(self.logger):
                raise e

        if not self.should_repaint():
            return

        if self.figure is None:
            self.create_figure()

            self._info.grid.axes.set_aspect("equal")
            self._time_text = self.figure.text(0.5, 0.01, self._time, ha="center")
            self.figure.show()
        else:
            self._time_text.set_text(self._time)

        first_plot = True
        if self._contours is not None:
            self._info.grid.axes.clear()
            self._info.grid.axes.set_title(self._title)
            first_plot = False

        axes_names = {name: i for i, name in enumerate(self._info.grid.axes_names)}
        axes_indices = [
            ax if isinstance(ax, int) else axes_names[ax]
            for ax in list(self._info.grid.axes)
        ]

        ax_1 = axes_indices[0]
        ax_2 = axes_indices[1]

        if isinstance(self._info.grid, fm.UnstructuredGrid):
            self._plot_unstructured(data, (ax_1, ax_2))
        else:
            self._plot_structured(data, (ax_1, ax_2))

        if first_plot:
            create_colorbar(self.figure, self._info.grid.axes, self._contours)
            self.figure.tight_layout()

        self.repaint(relim=False)

    def _plot_structured(self, data, axes):
        if axes != (0, 1) or axes != (1, 0):
            raise ValueError(f"Unsupported axes: {axes}")

        data_axes = [self._info.grid.data_axes[i] for i in axes]

        if self._fill:
            self._contours = self._info.grid.axes.contourf(
                *data_axes, data, **self.plot_kwargs
            )
        else:
            self._contours = self._info.grid.axes.contour(
                *data_axes, data, **self.plot_kwargs
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
                self._contours = self.axes.tricontourf(
                    *self.triangulation, data_flat, **self.plot_kwargs
                )
            else:
                self._contours = self.axes.tricontour(
                    *self.triangulation, data_flat, **self.plot_kwargs
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

                self._contours = self.axes.tripcolor(
                    *self._info.grid.points.T[list(axes)],
                    data_flat,
                    triangles=self._info.grid.cells,
                    **self.plot_kwargs,
                )
            else:
                if self.triangulation is None:
                    self.triangulation = [
                        Triangulation(*self._info.grid.data_points.T[list(axes)])
                    ]

                data_flat = np.ascontiguousarray(
                    data.reshape(-1, order=self._info.grid.order)
                )
                self._contours = self.axes.tricontour(
                    *self.triangulation, data_flat, **self.plot_kwargs
                )

    def _data_changed(self, _caller, time):
        if time is not None and not isinstance(time, datetime):
            with fm.tools.ErrorLogger(self.logger):
                raise ValueError("Time must be of type datetime")

        self._time = time

        self._plot()
