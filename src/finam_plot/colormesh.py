"""Raster image plot component for uniform and rectilinear grids."""
from datetime import datetime

import finam as fm
import matplotlib.pyplot as plt
import numpy as np


class ColorMeshPlot(fm.Component):
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
            axes=(0, 1),
            vmin=0, vmax=1, cmap="hsv", # plot kwargs
        )

    .. testcode:: constructor
        :hide:

        plot.initialize()

    Parameters
    ----------
    axes : (int, int) or (str, str), optional
        Tuple of axes indices or names. Default (0, 1).
    **plot_kwargs
        Keyword arguments passed to plot function. See :func:`matplotlib.pyplot.pcolormesh`.
    """

    def __init__(self, axes=(0, 1), **plot_kwargs):
        super().__init__()
        self._time = None
        self._figure = None
        self._plot_ax = None
        self._axes = axes
        self._info = None
        self._mesh = None
        self._plot_kwargs = plot_kwargs

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

        axes_names = {name: i for i, name in enumerate(self._info.grid.axes_names)}
        axes_indices = [
            ax if isinstance(ax, int) else axes_names[ax] for ax in list(self._axes)
        ]

        ax_1 = axes_indices[0]
        ax_2 = axes_indices[1]

        self._plot_image(data, (ax_1, ax_2))

        self._figure.show()
        self._figure.tight_layout()

        self._figure.canvas.draw()
        self._figure.canvas.flush_events()

    def _plot_image(self, data, axes):
        if axes == (0, 1):
            if self._info.grid.order == "F":
                data = data.transpose()
        elif axes == (1, 0):
            if self._info.grid.order == "C":
                data = data.transpose()
        else:
            raise ValueError(f"Unsupported axes: {axes}")

        if not self._info.grid.axes_increase[axes[0]]:
            data = np.flip(data, axis=axes[0])
        if not self._info.grid.axes_increase[axes[1]]:
            data = np.flip(data, axis=axes[1])

        data_axes = [self._info.grid.axes[i] for i in axes]

        if self._mesh is None:
            self._mesh = self._plot_ax.pcolormesh(
                data_axes[0],
                data_axes[1],
                data,
                **self._plot_kwargs,
            )
        else:
            self._mesh.set_array(data.ravel())

    def _data_changed(self, _caller, time):
        if time is not None and not isinstance(time, datetime):
            with fm.tools.ErrorLogger(self.logger):
                raise ValueError("Time must be of type datetime")

        self._time = time
        if self.status in (fm.ComponentStatus.UPDATED, fm.ComponentStatus.VALIDATED):
            self._update()
        else:
            self._plot()
