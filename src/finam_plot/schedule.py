"""Schedule visualization."""
from datetime import datetime

import finam as fm
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from .tools import create_figure


class SchedulePlot(fm.Component):
    """Live visualization of module update schedule.

    Takes inputs of arbitrary types and simply plots the time of notifications of each input.

    Uses :func:`matplotlib.pyplot.plot`.

    .. code-block:: text

                     +--------------+
        --> [custom] |              |
        --> [custom] | SchedulePlot |
        --> [......] |              |
                     +--------------+

    Note:
        This component is push-based without an internal time step.

    Examples
    --------

    .. testcode:: constructor

        import finam_plot as fmp

        plot = fmp.SchedulePlot(
            inputs=["Grid1", "Grid2"],
            colors=["red", "#ff00ee"],
            marker="o", lw=2.0, # plot kwargs
        )

    .. testcode:: constructor
        :hide:

        plot.initialize()

    Parameters
    ----------
    inputs : list of str
        Input names.
    title : str, optional
        Title for plot and window.
    colors : list of str, optional
        List of colors for the inputs. Uses matplotlib default colors by default.
    pos : tuple(number, number), optional
        Figure position. ``int`` is interpreted as pixels,
        ``float`` is interpreted as fraction of screen size.
    size : tuple(number, number), optional
        Figure size. ``int`` is interpreted as pixels,
        ``float`` is interpreted as fraction of screen size.
    **plot_kwargs
        Keyword arguments passed to plot function. See :func:`matplotlib.pyplot.plot`.
    """

    def __init__(
        self, inputs, title=None, colors=None, pos=None, size=None, **plot_kwargs
    ):
        super().__init__()
        self._figure = None
        self._axes = None
        self._lines = None
        self._x = [[] for _ in inputs]

        self._input_names = inputs
        self._title = title
        self._colors = colors or [e["color"] for e in plt.rcParams["axes.prop_cycle"]]

        self._bounds = (pos, size)
        self._plot_kwargs = plot_kwargs
        if "marker" not in self._plot_kwargs:
            self._plot_kwargs["marker"] = "+"

    def _initialize(self):
        """Initialize the component.

        After the method call, the component's inputs and outputs must be available,
        and the component should have status INITIALIZED.
        """
        for inp in self._input_names:
            self.inputs.add(
                fm.CallbackInput(self._data_changed, name=inp, time=None, grid=None)
            )

        self.create_connector()

    def _connect(self, start_time):
        """Push initial values to outputs.

        After the method call, the component should have status CONNECTED.
        """
        if self._figure is None:
            self._figure, self._axes = create_figure(self._bounds)

            self._figure.canvas.manager.set_window_title(self._title or "FINAM")
            self._axes.set_title(self._title)

            date_format = mdates.AutoDateFormatter(self._axes.xaxis)
            self._axes.xaxis.set_major_formatter(date_format)
            self._axes.tick_params(axis="x", labelrotation=20)
            self._axes.invert_yaxis()
            self._axes.set_yticks(range(len(self._input_names)))
            self._axes.set_yticklabels(self._input_names)

            self._figure.tight_layout()

        self.try_connect(start_time)

    def _validate(self):
        """Validate the correctness of the component's settings and coupling.

        After the method call, the component should have status VALIDATED.
        """
        self._figure.show()

    def _data_changed(self, caller, time):
        """Update for changed data.

        Parameters
        ----------
        caller
            Caller.
        time : datetime
            simulation time to get the data for.
        """
        self._update_plot(caller, time)

    def _update(self):
        """Update the component by one time step and push new values to outputs.

        After the method call, the component should have status UPDATED or FINISHED.
        """

    def _update_plot(self, caller, time):
        """Update the plot."""
        if self._lines is None:
            self._lines = [
                self._axes.plot(
                    [datetime.min],
                    i,
                    label=h,
                    c=self._colors[i % len(self._colors)],
                    **self._plot_kwargs,
                )[0]
                for i, h in enumerate(self._input_names)
            ]

        for i, inp in enumerate(self._input_names):
            if self.inputs[inp] == caller:
                self._x[i].append(time)

        for i, line in enumerate(self._lines):
            line.set_xdata(self._x[i])
            line.set_ydata(i)

        self._axes.relim()
        self._axes.autoscale_view(True, True, True)

        self._figure.canvas.draw()
        self._figure.canvas.flush_events()

    def _finalize(self):
        """Finalize and clean up the component.

        After the method call, the component should have status FINALIZED.
        """
