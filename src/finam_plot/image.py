"""Raster image plot component for uniform grids."""
from datetime import datetime

import finam as fm
import numpy as np

from .plot import PlotBase
from .tools import create_colorbar


class ImagePlot(PlotBase):
    """Raster image plot component for uniform grids.

    Data must be of grid type :class:`finam.UniformGrid` or :class:`finam.EsriGrid`.

    Uses :func:`matplotlib.pyplot.imshow`.

    .. code-block:: text

                   +-------------+
                   |             |
        --> [Grid] |  ImagePlot  |
                   |             |
                   +-------------+

    Note:
        This component is push-based without an internal time step.

    Examples
    --------

    .. testcode:: constructor

        import finam_plot as fmp

        plot = fmp.ImagePlot(
            axes=(0, 1),
            vmin=0, vmax=1, cmap="hsv", # plot kwargs
        )

    .. testcode:: constructor
        :hide:

        plot.initialize()

    Parameters
    ----------
    title : str, optional
        Title for plot and window.
    axes : (int, int) or (str, str), optional
        Tuple of axes indices or names. Default (0, 1).
    pos : tuple(number, number), optional
        Figure position. ``int`` is interpreted as pixels,
        ``float`` is interpreted as fraction of screen size.
    size : tuple(number, number), optional
        Figure size. ``int`` is interpreted as pixels,
        ``float`` is interpreted as fraction of screen size.
    update_interval : int, optional
         Redraw interval, in number of push steps.
    **plot_kwargs
        Keyword arguments passed to plot function. See :func:`matplotlib.pyplot.imshow`.
    """

    def __init__(
        self,
        title=None,
        axes=(0, 1),
        pos=None,
        size=None,
        update_interval=1,
        **plot_kwargs,
    ):
        super().__init__(title, pos, size, update_interval, **plot_kwargs)
        self._time = None
        self._axes_order = axes
        self._info = None
        self._image = None
        self._extent = None
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
                if isinstance(self._info.grid, fm.UniformGrid):
                    if self._info.grid.dim != 2:
                        raise ValueError(
                            "Only 2-D UniformGrid is supported in image plot."
                        )
                else:
                    raise ValueError("Only UniformGrid is supported in image plot.")

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

        axes_names = {name: i for i, name in enumerate(self._info.grid.axes_names)}
        axes_indices = [
            ax if isinstance(ax, int) else axes_names[ax]
            for ax in list(self._axes_order)
        ]

        ax_1 = axes_indices[0]
        ax_2 = axes_indices[1]

        if self.figure is None:
            self.create_figure()
            self.axes.set_aspect("equal")

            g = self._info.grid
            self._extent = []

            self._extent[0:1] = (
                [g.axes[ax_1][0], g.axes[ax_1][-1]]
                if g.data_location == fm.Location.CELLS
                else [
                    g.axes[ax_1][0] - g.spacing[ax_1] / 2,
                    g.axes[ax_1][-1] + g.spacing[ax_1] / 2,
                ]
            )
            self._extent[2:3] = (
                [g.axes[ax_2][0], g.axes[ax_2][-1]]
                if g.data_location == fm.Location.CELLS
                else [
                    g.axes[ax_2][0] - g.spacing[ax_2] / 2,
                    g.axes[ax_2][-1] + g.spacing[ax_2] / 2,
                ]
            )
            self.figure.show()

        self._plot_image(data, (ax_1, ax_2))

        self.repaint(relim=False)

    def _plot_image(self, data, axes):
        if axes == (0, 1):
            data = data.transpose()
        elif axes == (1, 0):
            pass
        else:
            raise ValueError(f"Unsupported axes: {axes}")

        if not self._info.grid.axes_increase[axes[0]]:
            data = np.flip(data, axis=axes[0])
        if not self._info.grid.axes_increase[axes[1]]:
            data = np.flip(data, axis=axes[1])

        if self._image is None:
            self._image = self.axes.imshow(
                data,
                interpolation=None,
                origin="lower",
                extent=self._extent,
                **self.plot_kwargs,
            )
            self._time_text = self.figure.text(0.5, 0.01, self._time, ha="center")

            create_colorbar(self.figure, self.axes, self._image)
            self.figure.tight_layout()
        else:
            self._image.set_data(data)
            self._time_text.set_text(self._time)

    def _data_changed(self, _caller, time):
        if time is not None and not isinstance(time, datetime):
            with fm.tools.ErrorLogger(self.logger):
                raise ValueError("Time must be of type datetime")

        self._time = time

        self._plot()
