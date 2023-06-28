"""Components for plotting grid specifications"""
import math

import finam as fm
import matplotlib.pyplot as plt

from .tools import create_figure


class GridSpecPlot(fm.Component):
    """Plots the geometry of grid specifications

    Uses :func:`matplotlib.pyplot.plot` and :func:`matplotlib.pyplot.scatter`.

    .. code-block:: text

                     +--------------+
        --> [custom] |              |
        --> [custom] | GridSpecPlot |
        --> [......] |              |
                     +--------------+

    Note:
        This component is push-based without an internal time step.

    Examples
    --------

    .. testcode:: constructor

        import finam_plot as fmp

        plot = fmp.GridSpecPlot(
            inputs=["Grid1", "Grid2"],
            colors=["red", "#ff00ee"],
        )

    .. testcode:: constructor
        :hide:

        plot.initialize()

    Parameters
    ----------
    inputs : list
        List on input names.
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
    """

    def __init__(self, inputs, title=None, colors=None, pos=None, size=None):
        super().__init__()
        self._figure = None
        self._names = inputs
        self._title = title
        self._colors = colors or [e["color"] for e in plt.rcParams["axes.prop_cycle"]]
        self._bounds = (pos, size)
        self._infos = {name: None for name in self._names}

    def _initialize(self):
        for name in self._names:
            self.inputs.add(
                io=fm.CallbackInput(
                    name=name,
                    callback=self._data_changed,
                    time=None,
                    grid=None,
                    units=None,
                )
            )
        self.create_connector()

    def _connect(self, start_time):
        self.try_connect(start_time)
        for name, val in self._connector.in_infos.items():
            if val is not None:
                self._infos[name] = val

    def _validate(self):
        self._update_plot()

    def _update(self):
        pass

    def _update_plot(self):
        self._figure, axes = create_figure(self._bounds)
        axes.set_aspect("equal")

        self._figure.canvas.manager.set_window_title(self._title or "FINAM")
        axes.set_title(self._title)

        for i, name in enumerate(self._infos):
            self._plot_grid(axes, name, self._colors[i % len(self._colors)])

        self._figure.show()
        self._figure.tight_layout()
        self._figure.canvas.draw()
        self._figure.canvas.flush_events()

    def _finalize(self):
        pass

    def _plot_grid(self, axes, name, color):
        info = self._infos[name]
        data_points = info.grid.data_points
        points = info.grid.points
        cells = info.grid.cells

        if not isinstance(info.grid, fm.UnstructuredPoints):
            self._plot_cells(axes, points, cells, color)

        axes.scatter(*data_points.T[:2], marker="+", c=color)

        if not isinstance(info.grid, fm.data.StructuredGrid):
            return

        axes_inc = info.grid.axes_increase[:2]
        x_axis = info.grid.axes[0]
        y_axis = info.grid.axes[1]
        if not axes_inc[0]:
            x_axis = x_axis[::-1]
        if not axes_inc[1]:
            y_axis = y_axis[::-1]
        x = x_axis[0]
        y = y_axis[0]
        len_x = x_axis[-1] - x
        len_y = y_axis[-1] - y
        length_abs = 0.25 * min(abs(len_x), abs(len_y))
        len_x = math.copysign(length_abs, len_x)
        len_y = math.copysign(length_abs, len_y)
        axes.arrow(
            x,
            y,
            len_x,
            0,
            fc=color,
            head_width=0.05 * length_abs,
            length_includes_head=True,
        )
        axes.arrow(
            x,
            y,
            0,
            len_y,
            fc=color,
            head_width=0.05 * length_abs,
            length_includes_head=True,
        )

    def _plot_cells(self, axes, points, cells, color):
        for nodes in cells:
            for i, node in enumerate(nodes):
                pt1 = points[node]
                pt2 = points[nodes[(i + 1) % len(nodes)]]
                axes.plot(
                    [pt1[0], pt2[0]],
                    [pt1[1], pt2[1]],
                    c=color,
                    lw=0.5,
                )

    def _data_changed(self, _caller, _time):
        pass
        # self.update()
