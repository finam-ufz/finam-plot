"""Time series visualization."""
from datetime import datetime, timedelta

import finam as fm
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

from .plot import PlotBase
from .tools import create_figure


class TimeSeriesPlot(PlotBase):
    """Line plot for multiple time series, push-based.

    Expects all inputs to be scalar values.

    Uses :func:`matplotlib.pyplot.plot`.

    .. code-block:: text

                     +----------------+
        --> [custom] |                |
        --> [custom] | TimeSeriesPlot |
        --> [......] |                |
                     +----------------+

    Note:
        This component is push-based without an internal time step.

    Examples
    --------

    .. testcode:: constructor

        import finam_plot as fmp

        plot = fmp.TimeSeriesPlot(
            inputs=["Value1", "Value2"],
            colors=["red", "#ff00ee"],
            marker="o", lw=2.0, # plot kwargs
        )

    .. testcode:: constructor
        :hide:

        plot.initialize()

    Parameters
    ----------
    inputs : list of str or dict of str, str
        List of input names (plot series) that will become available for coupling.
        Can also be a dictionary with units as values.
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
    update_interval : int, optional
         Redraw interval (independent of data retrieval).
    **plot_kwargs
        Keyword arguments passed to plot function. See :func:`matplotlib.pyplot.plot`.
    """

    def __init__(
        self,
        inputs,
        title=None,
        colors=None,
        pos=None,
        size=None,
        update_interval=1,
        **plot_kwargs,
    ):
        super().__init__(title, pos, size, update_interval, **plot_kwargs)
        self._time = None
        self._caller = None

        self._data = [[] for _ in inputs]
        self._x = [[] for _ in inputs]
        self._lines = None

        self._input_units = (
            inputs if isinstance(inputs, dict) else {n: None for n in inputs}
        )
        self._colors = colors or [e["color"] for e in plt.rcParams["axes.prop_cycle"]]

    def _initialize(self):
        """Initialize the component.

        After the method call, the component's inputs and outputs must be available,
        and the component should have status INITIALIZED.
        """
        for inp, units in self._input_units.items():
            self.inputs.add(
                fm.CallbackInput(
                    self._data_changed,
                    name=inp,
                    time=None,
                    grid=fm.NoGrid(),
                    units=units,
                )
            )

        self.create_connector(pull_data=self._input_units.keys())

    def _connect(self, start_time):
        """Push initial values to outputs.

        After the method call, the component should have status CONNECTED.
        """
        if self.figure is None:
            with plt.style.context("fast"):
                self.create_figure()

                date_format = mdates.AutoDateFormatter(self.axes.xaxis)
                self.axes.xaxis.set_major_formatter(date_format)
                self.axes.tick_params(axis="x", labelrotation=20)

                self.figure.tight_layout()

        self.try_connect(start_time)

    def _validate(self):
        """Validate the correctness of the component's settings and coupling.

        After the method call, the component should have status VALIDATED.
        """
        self._caller = None
        self._update_plot()
        self.figure.show()

    def _data_changed(self, caller, time):
        """Update for changed data.

        Parameters
        ----------
        caller
            Caller.
        time : datetime
            simulation time to get the data for.
        """
        if self._time != time:
            if self.should_repaint():
                self.repaint(relim=True)

        self._caller = caller
        self._time = time

        if self.status in (fm.ComponentStatus.UPDATED, fm.ComponentStatus.VALIDATED):
            self._update_plot()

    def _update_plot(self):
        with plt.style.context("fast"):
            if self._lines is None:
                self._lines = []
                for i, n in enumerate(self._input_units):
                    units = self.inputs[n].info.meta.get("units")
                    units = f" [{units}]" if units else ""
                    self._lines.append(
                        self.axes.plot(
                            [],
                            [],
                            label=n + units,
                            c=self._colors[i % len(self._colors)],
                            **self.plot_kwargs,
                        )[0]
                    )
                self.axes.legend(loc=1)

            for i, inp in enumerate(self._input_units):
                if self._caller is None or self.inputs[inp] == self._caller:
                    value = fm.data.get_magnitude(
                        self.inputs[inp].pull_data(self._time)
                    )

                    self._x[i].append(self._time)
                    self._data[i].append(value.item())

                    self._lines[i].set_xdata(self._x[i])
                    self._lines[i].set_ydata(self._data[i])

    def _finalize(self):
        """Finalize and clean up the component.

        After the method call, the component should have status FINALIZED.
        """
        self.repaint(relim=True)


class StepTimeSeriesPlot(fm.TimeComponent):
    """Line plot for multiple time series, with internal time step.

    Expects all inputs to be scalar values.

    This component has an internal time step.
    For a push-based line series plot, see :class:`.TimeSeriesPlot`.

    Uses :func:`matplotlib.pyplot.plot`.

    .. code-block:: text

                     +----------------+
        --> [custom] |                |
        --> [custom] | TimeSeriesPlot |
        --> [......] |                |
                     +----------------+

    Examples
    --------

    .. testcode:: constructor

        import datetime as dt
        import finam_plot as fmp

        plot = fmp.StepTimeSeriesPlot(
            inputs=["Value1", "Value2"],
            colors=["red", "#ff00ee"],
            start=dt.datetime(2000, 1, 1),
            step=dt.timedelta(days=1),
            marker="o", lw=2.0, # plot kwargs
        )

    .. testcode:: constructor
        :hide:

        plot.initialize()

    Parameters
    ----------
    inputs : list of str or dict of str, str
        List of input names (plot series) that will become available for coupling.
        Can also be a dictionary with units as values.
    start : datetime
        Starting time.
    step : timedelta
        Time step.
    title : str, optional
        Title for plot and window.
    colors : list of str, optional
        List of colors for the inputs. Uses matplotlib default colors by default.
    intervals : list of int or None, optional
        List of interval values to interleave data retrieval of certain inputs.
        Values are numbers of updates, i.e. whole-numbered factors for ``step``.
    update_interval : int, optional
         Redraw interval (independent of data retrieval).
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
        self,
        inputs,
        start,
        step,
        title=None,
        colors=None,
        intervals=None,
        update_interval=1,
        pos=None,
        size=None,
        **plot_kwargs,
    ):
        super().__init__()
        with fm.tools.ErrorLogger(self.logger):
            if not isinstance(start, datetime):
                raise ValueError("Start must be of type datetime")
            if not isinstance(step, timedelta):
                raise ValueError("Step must be of type timedelta")

        self._step = step
        self._update_interval = update_interval
        self._intervals = intervals if intervals else [1 for _ in inputs]
        self._time = start
        self._updates = 0
        self._figure = None
        self._axes = None
        self._data = [[] for _ in inputs]
        self._x = [[] for _ in inputs]
        self._lines = None

        self._input_units = (
            inputs if isinstance(inputs, dict) else {n: None for n in inputs}
        )
        self._title = title
        self._bounds = (pos, size)
        self._plot_kwargs = plot_kwargs
        self._colors = colors or [e["color"] for e in plt.rcParams["axes.prop_cycle"]]

    @property
    def next_time(self):
        """The component's predicted simulation time of the next pulls."""
        return self.time + self._step

    def _initialize(self):
        """Initialize the component.

        After the method call, the component's inputs and outputs must be available,
        and the component should have status INITIALIZED.
        """
        for inp, units in self._input_units.items():
            self.inputs.add(name=inp, time=self.time, grid=fm.NoGrid(), units=units)

        self.create_connector()

    def _connect(self, start_time):
        """Push initial values to outputs.

        After the method call, the component should have status CONNECTED.
        """
        self.try_connect(start_time)

    def _validate(self):
        """Validate the correctness of the component's settings and coupling.

        After the method call, the component should have status VALIDATED.
        """
        with plt.style.context("fast"):
            self._figure, self._axes = create_figure(self._bounds)

            self._figure.canvas.manager.set_window_title(self._title or "FINAM")
            self._axes.set_title(self._title)

            date_format = mdates.AutoDateFormatter(self._axes.xaxis)
            self._axes.xaxis.set_major_formatter(date_format)
            self._axes.tick_params(axis="x", labelrotation=20)

            self._figure.show()

    def _update(self):
        """Update the component by one time step.
        Push new values to outputs.

        After the method call, the component should have status UPDATED or FINISHED.
        """
        self._time += self._step

        with plt.style.context("fast"):
            if self._lines is None:
                self._lines = []
                for i, n in enumerate(self._input_units):
                    units = self.inputs[n].info.meta.get("units")
                    units = f" [{units}]" if units else ""
                    self._lines.append(
                        self._axes.plot(
                            [],
                            [],
                            label=n + units,
                            c=self._colors[i % len(self._colors)],
                            **self._plot_kwargs,
                        )[0]
                    )
                self._axes.legend(loc=1)

            for i, inp in enumerate(self._input_units):
                if self._updates % self._intervals[i] == 0:
                    value = fm.data.get_magnitude(self.inputs[inp].pull_data(self.time))

                    self._x[i].append(self.time)
                    self._data[i].append(value.item())

            if self._updates % self._update_interval == 0:
                for i, line in enumerate(self._lines):
                    line.set_xdata(self._x[i])
                    line.set_ydata(self._data[i])
                self._repaint()

        self._updates += 1

    def _repaint(self):
        self._axes.relim()
        self._axes.autoscale_view(True, True, True)

        self._figure.canvas.draw_idle()
        self._figure.canvas.flush_events()

    def _finalize(self):
        """Finalize and clean up the component.

        After the method call, the component should have status FINALIZED.
        """
        self._repaint()
