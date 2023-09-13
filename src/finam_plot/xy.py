"""Time series visualization."""
import finam as fm
import matplotlib.pyplot as plt

from .plot import PlotBase


class XyPlot(PlotBase):
    """Line and scatter plots for multiple instant series, push-based.

    Inputs are expected to be one of:

    * 1-D structured grids. The axis is plotted as x, while the data is plotted as y.
    * 1-D NoGrid. x is enumerated, data is plotted as y.
    * 2-D NoGrid. x is the first column, while y is the second column.

    Uses :func:`matplotlib.pyplot.plot`.

    .. code-block:: text

                     +----------+
        --> [custom] |          |
        --> [custom] |  XyPlot  |
        --> [......] |          |
                     +----------+

    Note:
        This component is push-based without an internal time step.

    Examples
    --------

    .. testcode:: constructor

        import finam_plot as fmp

        plot = fmp.XyPlot(
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

        self._lines = None
        self._infos = None

        self._input_names = inputs
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
                    grid=None,
                    units=None,
                )
            )

        self.create_connector()

    def _connect(self, start_time):
        """Push initial values to outputs.

        After the method call, the component should have status CONNECTED.
        """
        if self.figure is None:
            self.create_figure()

            self.figure.tight_layout()
            self.figure.show()

        self.try_connect(start_time)

        if self.status == fm.ComponentStatus.CONNECTED:
            self._infos = dict(self.connector.in_infos)

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
        time : datetime.datetime
            simulation time to get the data for.
        """
        if self._time != time:
            if self.should_repaint():
                self.repaint(relim=True)

        self._caller = caller
        self._time = time

        self._update_plot()

    def _update_plot(self):
        if self._lines is None:
            self._lines = [
                self.axes.plot(
                    [],
                    [],
                    label=n,
                    c=self._colors[i % len(self._colors)],
                    **self.plot_kwargs,
                )[0]
                for i, n in enumerate(self._input_names)
            ]
            self.axes.legend(loc=1)

        for i, inp in enumerate(self._input_names):
            if self.inputs[inp] == self._caller:
                value = self.inputs[inp].pull_data(self._time)

                x, y = self._extract_data(self._infos[inp].grid, value)

                self._lines[i].set_xdata(x)
                self._lines[i].set_ydata(y)

    def _extract_data(self, grid, data):
        raw = fm.data.get_magnitude(data)[0, ...]
        if isinstance(grid, fm.NoGrid):
            if grid.dim == 1:
                return list(range(raw.shape[0])), raw

            return raw[:, 0], raw[:, 1]

        if isinstance(grid, fm.data.StructuredGrid):
            return grid.data_axes[0], raw

        with fm.tools.ErrorLogger(self.logger):
            raise ValueError(f"Grid type {grid.__class__.__name__} not supported.")

    def _finalize(self):
        """Finalize and clean up the component.

        After the method call, the component should have status FINALIZED.
        """
        self.repaint(relim=True)
