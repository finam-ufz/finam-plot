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

            self.axes.set_aspect("equal")
            self._time_text = self.figure.text(0.5, 0.01, self._time, ha="center")
            self.figure.show()
        else:
            self._time_text.set_text(self._time)

        first_plot = True
        if self._contours is not None:
            self.axes.clear()
            self.axes.set_title(self._title)
            first_plot = False

        if isinstance(self._info.grid, fm.UnstructuredGrid):
            self._plot_unstructured(data)
        else:
            self._plot_structured(data)

        if first_plot:
            create_colorbar(self.figure, self.axes, self._contours)
            self.figure.tight_layout()

        self.repaint(relim=False)

    def _plot_structured(self, data):
        g = self._info.grid
        data = g.to_canonical(data).T
        axes = g.cell_axes if g.data_location == fm.Location.CELLS else g.axes
        if self._fill:
            self._contours = self.axes.contourf(*axes[:2], data, **self.plot_kwargs)
        else:
            self._contours = self.axes.contour(*axes[:2], data, **self.plot_kwargs)

    def _plot_unstructured(self, data):
        g = self._info.grid
        if g.data_location == fm.Location.POINTS:
            needs_triangulation = isinstance(g, fm.UnstructuredPoints) or any(
                tp != fm.CellType.TRI.value for tp in g.cell_types
            )

            if needs_triangulation and not self._triangulate:
                with fm.tools.ErrorLogger(self.logger):
                    raise ValueError(
                        "Data requires triangulation. Use with `triangulate=True`"
                    )

            if self.triangulation is None:
                if self._triangulate:
                    self.triangulation = [Triangulation(*g.data_points.T[:2])]
                else:
                    self.triangulation = [
                        *g.data_points.T[:2],
                        g.cells,
                    ]

            data_flat = np.ascontiguousarray(data.reshape(-1, order=g.order))
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
                tris_only = all(tp == fm.CellType.TRI.value for tp in g.cell_types)

                if not tris_only:
                    with fm.tools.ErrorLogger(self.logger):
                        raise NotImplementedError(
                            "Contour plots for cell data are only supported for triangular meshes"
                        )

                data_flat = np.ascontiguousarray(data.reshape(-1, order=g.order))

                self._contours = self.axes.tripcolor(
                    *g.points.T[:2],
                    data_flat,
                    triangles=g.cells,
                    **self.plot_kwargs,
                )
            else:
                if self.triangulation is None:
                    self.triangulation = [Triangulation(*g.data_points.T[:2])]

                data_flat = np.ascontiguousarray(data.reshape(-1, order=g.order))
                self._contours = self.axes.tricontour(
                    *self.triangulation, data_flat, **self.plot_kwargs
                )

    def _data_changed(self, _caller, time):
        if time is not None and not isinstance(time, datetime):
            with fm.tools.ErrorLogger(self.logger):
                raise ValueError("Time must be of type datetime")

        self._time = time

        self._plot()
