"""Raster image plot component for uniform and rectilinear grids."""
from datetime import datetime

import finam as fm

from .plot import PlotBase
from .tools import create_colorbar


class ColorMeshPlot(PlotBase):
    """Raster image plot component for uniform and rectilinear grids.

    Data must be of grid type :class:`finam.RectilinearGrid`, :class:`finam.UniformGrid`
    or :class:`finam.EsriGrid`.

    Uses :func:`matplotlib.pyplot.pcolormesh`.

    .. code-block:: text

                   +---------------+
                   |               |
        --> [Grid] | ColorMeshPlot |
                   |               |
                   +---------------+

    Note:
        This component is push-based without an internal time step.

    Examples
    --------

    .. testcode:: constructor

        import finam_plot as fmp

        plot = fmp.ColorMeshPlot(
            vmin=0, vmax=1, cmap="hsv", # plot_kwargs
        )

    .. testcode:: constructor
        :hide:

        plot.initialize()

    Parameters
    ----------
    title : str, optional
        Title for plot and window.
    pos : tuple(number, number), optional
        Figure position. ``int`` is interpreted as pixels,
        ``float`` is interpreted as fraction of screen size.
    size : tuple(number, number), optional
        Figure size. ``int`` is interpreted as pixels,
        ``float`` is interpreted as fraction of screen size.
    update_interval : int, optional
         Redraw interval, in number of push steps.
    **plot_kwargs
        Keyword arguments passed to plot function. See :func:`matplotlib.pyplot.pcolormesh`.
    """

    def __init__(
        self,
        title=None,
        pos=None,
        size=None,
        update_interval=1,
        **plot_kwargs,
    ):
        super().__init__(title, pos, size, update_interval, **plot_kwargs)
        self._time = None
        self._info = None
        self._mesh = None
        self._time_text = None

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
            with fm.tools.ErrorLogger(self.logger):
                if isinstance(self._info.grid, fm.RectilinearGrid):
                    if self._info.grid.dim != 2:
                        raise ValueError(
                            "Only 2-D RectilinearGrid is supported in colormesh plot."
                        )
                else:
                    raise ValueError(
                        "Only RectilinearGrid is supported in colormesh plot."
                    )

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

        if self.figure is None:
            self.create_figure()
            self.axes.set_aspect("equal")
            self.figure.show()

        if not self.should_repaint():
            return

        self._plot_image(data)
        self.repaint(relim=False)

    def _plot_image(self, data):
        g = self._info.grid
        data = g.to_canonical(data).T
        if self._mesh is None:
            self._mesh = self.axes.pcolormesh(
                g.axes[0],
                g.axes[1],
                data,
                **self.plot_kwargs,
            )
            self._time_text = self.figure.text(0.5, 0.01, self._time, ha="center")
            create_colorbar(self.figure, self.axes, self._mesh)
            self.figure.tight_layout()
        else:
            self._mesh.set_array(data.ravel())
            self._time_text.set_text(self._time)

    def _data_changed(self, _caller, time):
        if time is not None and not isinstance(time, datetime):
            with fm.tools.ErrorLogger(self.logger):
                raise ValueError("Time must be of type datetime")

        self._time = time

        self._plot()
