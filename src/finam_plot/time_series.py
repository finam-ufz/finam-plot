"""Time series visualization."""
from datetime import datetime, timedelta

import finam as fm
import matplotlib.dates as mdates
import matplotlib.pyplot as plt


class TimeSeriesPlot(fm.Component):
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
    inputs : list of str
        List of input names (plot series) that will become available for coupling.
    colors : list of str, optional
        List of colors for the inputs. Uses matplotlib default colors by default.
    **plot_kwargs
        Keyword arguments passed to plot function. See :func:`matplotlib.pyplot.plot`.
    """

    def __init__(self, inputs, colors=None, **plot_kwargs):
        super().__init__()
        self._time = None
        self._caller = None

        self._figure = None
        self._axes = None
        self._data = [[] for _ in inputs]
        self._x = [[] for _ in inputs]
        self._lines = None

        self._input_names = inputs
        self._plot_kwargs = plot_kwargs
        self._colors = colors or [e["color"] for e in plt.rcParams["axes.prop_cycle"]]

    def _initialize(self):
        """Initialize the component.

        After the method call, the component's inputs and outputs must be available,
        and the component should have status INITIALIZED.
        """
        for inp in self._input_names:
            self.inputs.add(
                fm.CallbackInput(
                    self._data_changed,
                    name=inp,
                    time=None,
                    grid=fm.NoGrid(),
                    units=None,
                )
            )

        self._figure, self._axes = plt.subplots()
        date_format = mdates.AutoDateFormatter(self._axes.xaxis)
        self._axes.xaxis.set_major_formatter(date_format)
        self._axes.tick_params(axis="x", labelrotation=20)

        self._figure.tight_layout()
        self._figure.show()

        self.create_connector()

    def _connect(self):
        """Push initial values to outputs.

        After the method call, the component should have status CONNECTED.
        """
        self.try_connect()

    def _validate(self):
        """Validate the correctness of the component's settings and coupling.

        After the method call, the component should have status VALIDATED.
        """
        self._update_plot()

    def _data_changed(self, caller, time):
        """Update for changed data.

        Parameters
        ----------
        caller
            Caller.
        time : datetime
            simulation time to get the data for.
        """
        self._caller = caller
        self._time = time

        if self.status in (fm.ComponentStatus.UPDATED, fm.ComponentStatus.VALIDATED):
            self.update()
        else:
            self._update_plot()

    def _update(self):
        """Update the component by one time step and push new values to outputs.

        After the method call, the component should have status UPDATED or FINISHED.
        """
        self._update_plot()

    def _update_plot(self):
        if self._lines is None:
            self._lines = [
                self._axes.plot(
                    [],
                    [],
                    label=h,
                    c=self._colors[i % len(self._colors)],
                    **self._plot_kwargs,
                )[0]
                for i, h in enumerate(self._input_names)
            ]
            self._axes.legend(loc=1)

        for i, inp in enumerate(self._input_names):
            if self.inputs[inp] == self._caller:
                value = fm.data.get_magnitude(
                    fm.data.strip_time(self.inputs[inp].pull_data(self._time))
                )

                self._x[i].append(self._time)
                self._data[i].append(value)

        for i, line in enumerate(self._lines):
            line.set_xdata(self._x[i])
            line.set_ydata(self._data[i])

        self._axes.relim()
        self._axes.autoscale_view(True, True, True)

        self._figure.canvas.draw()
        self._figure.canvas.flush_events()

    def _finalize(self):
        """Finalize and clean up the component.

        After the method call, the component should have status FINALIZED.
        """


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
    inputs : list of str
        List of input names (plot series) that will become available for coupling.
    start : datetime
        Starting time.
    step : timedelta
        Time step.
    colors : list of str, optional
        List of colors for the inputs. Uses matplotlib default colors by default.
    intervals : list of int or None, optional
        List of interval values to interleave data retrieval of certain inputs.
        Values are numbers of updates, i.e. whole-numbered factors for ``step``.
    update_interval : int, optional
         Redraw interval (independent of data retrieval).
    **plot_kwargs
        Keyword arguments passed to plot function. See :func:`matplotlib.pyplot.plot`.
    """

    def __init__(
        self,
        inputs,
        start,
        step,
        colors=None,
        intervals=None,
        update_interval=1,
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

        self._input_names = inputs
        self._plot_kwargs = plot_kwargs
        self._colors = colors or [e["color"] for e in plt.rcParams["axes.prop_cycle"]]

    @property
    def next_time(self):
        return self.time + self._step

    def _initialize(self):
        """Initialize the component.

        After the method call, the component's inputs and outputs must be available,
        and the component should have status INITIALIZED.
        """
        for inp in self._input_names:
            self.inputs.add(name=inp)

        self._figure, self._axes = plt.subplots()
        date_format = mdates.AutoDateFormatter(self._axes.xaxis)
        self._axes.xaxis.set_major_formatter(date_format)
        self._axes.tick_params(axis="x", labelrotation=20)

        self._figure.show()

        self.create_connector()

    def _connect(self):
        """Push initial values to outputs.

        After the method call, the component should have status CONNECTED.
        """
        self.try_connect(
            exchange_infos={
                name: fm.Info(time=self.time, grid=fm.NoGrid()) for name in self.inputs
            }
        )

    def _validate(self):
        """Validate the correctness of the component's settings and coupling.

        After the method call, the component should have status VALIDATED.
        """

    def _update(self):
        """Update the component by one time step.
        Push new values to outputs.

        After the method call, the component should have status UPDATED or FINISHED.
        """
        self._time += self._step

        if self._lines is None:
            self._lines = [
                self._axes.plot(
                    [],
                    [],
                    label=h,
                    c=self._colors[i % len(self._colors)],
                    **self._plot_kwargs,
                )[0]
                for i, h in enumerate(self._input_names)
            ]
            self._axes.legend(loc=1)

        for i, inp in enumerate(self._input_names):
            if self._updates % self._intervals[i] == 0:
                value = fm.data.get_magnitude(
                    fm.data.strip_time(self.inputs[inp].pull_data(self.time))
                )

                self._x[i].append(self.time)
                self._data[i].append(value)

        if self._updates % self._update_interval == 0:
            for i, line in enumerate(self._lines):
                line.set_xdata(self._x[i])
                line.set_ydata(self._data[i])

            self._axes.relim()
            self._axes.autoscale_view(True, True, True)

            self._figure.canvas.draw()
            self._figure.canvas.flush_events()

        self._updates += 1

    def _finalize(self):
        """Finalize and clean up the component.

        After the method call, the component should have status FINALIZED.
        """
