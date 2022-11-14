"""Time series visualization."""
import finam as fm
import matplotlib.pyplot as plt

from .tools import convert_pos, convert_size, move_figure


class XyPlot(fm.Component):
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
    **plot_kwargs
        Keyword arguments passed to plot function. See :func:`matplotlib.pyplot.plot`.
    """

    def __init__(
        self, inputs, title=None, colors=None, pos=None, size=None, **plot_kwargs
    ):
        super().__init__()
        self._time = None
        self._caller = None

        self._figure = None
        self._axes = None
        self._lines = None
        self._infos = None

        self._input_names = inputs
        self._title = title
        self._bounds = (convert_pos(pos), convert_size(size))
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
                    grid=None,
                    units=None,
                )
            )

        self._figure, self._axes = plt.subplots(figsize=self._bounds[1])
        move_figure(self._figure, self._bounds[0])

        self._figure.tight_layout()
        self._figure.show()

        self.create_connector()

    def _connect(self):
        """Push initial values to outputs.

        After the method call, the component should have status CONNECTED.
        """
        self.try_connect()

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
                    label=n,
                    c=self._colors[i % len(self._colors)],
                    **self._plot_kwargs,
                )[0]
                for i, n in enumerate(self._input_names)
            ]
            self._axes.legend(loc=1)

        for i, inp in enumerate(self._input_names):
            if self.inputs[inp] == self._caller:
                value = self.inputs[inp].pull_data(self._time)

                x, y = self._extract_data(self._infos[inp].grid, value)

                self._lines[i].set_xdata(x)
                self._lines[i].set_ydata(y)

        self._axes.relim()
        self._axes.autoscale_view(True, True, True)

        self._figure.canvas.draw()
        self._figure.canvas.flush_events()

    def _finalize(self):
        """Finalize and clean up the component.

        After the method call, the component should have status FINALIZED.
        """

    def _extract_data(self, grid, data):
        raw = fm.data.get_magnitude(fm.data.strip_time(data))
        if isinstance(grid, fm.NoGrid):
            if grid.dim == 1:
                return list(range(raw.shape[0])), raw

            return raw[:, 0], raw[:, 1]

        if isinstance(grid, fm.data.grid_tools.StructuredGrid):
            return grid.data_axes[0], raw

        with fm.tools.ErrorLogger(self.logger):
            raise ValueError(f"Grid type {grid.__class__.__name__} not supported.")
