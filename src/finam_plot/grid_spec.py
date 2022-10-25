"""Components for plotting grid specifications"""
import math

import finam as fm
import matplotlib.pyplot as plt


class GridSpecPlot(fm.Component):
    """Plots the geometry of grid specifications"""

    def __init__(self, inputs, axes=(0, 1), colors="black"):
        super().__init__()
        self._figure = None
        self._names = inputs

        if isinstance(axes, list):
            if len(axes) != len(self._names):
                raise ValueError(
                    "Axes must be a tuple or a list of tuples with the same length as the inputs"
                )
            self._axes = dict(zip(self._names, axes))
        else:
            self._axes = dict(zip(self._names, [axes] * len(self._names)))

        if isinstance(colors, list):
            if len(colors) != len(self._names):
                raise ValueError(
                    "Colors must be a string or a list of strings with the same length as the inputs"
                )
            self._colors = dict(zip(self._names, colors))
        else:
            self._colors = dict(zip(self._names, [colors] * len(self._names)))

        self._infos = {name: None for name in self._names}

        self.drawn = False

        self.status = fm.ComponentStatus.CREATED

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

    def _connect(self):
        self.try_connect()
        for name, val in self._connector.in_infos.items():
            if val is not None:
                self._infos[name] = val

    def _validate(self):
        pass

    def _update(self):
        if self.drawn or self.status != fm.ComponentStatus.VALIDATED:
            return

        self.drawn = True

        self._figure, axes = plt.subplots()
        axes.set_aspect("equal")

        for name, _ in self._infos.items():
            self._plot_grid(axes, name)

        self._figure.show()
        self._figure.tight_layout()
        self._figure.canvas.draw()
        self._figure.canvas.flush_events()

    def _finalize(self):
        pass

    def _plot_grid(self, axes, name):
        info = self._infos[name]
        data_points = info.grid.data_points
        points = info.grid.points
        cells = info.grid.cells

        color = self._colors[name]

        axes_names = {name: i for i, name in enumerate(info.grid.axes_names)}
        axes_indices = [
            ax if isinstance(ax, int) else axes_names[ax]
            for ax in list(self._axes[name])
        ]

        ax_1 = axes_indices[0]
        ax_2 = axes_indices[1]

        if not isinstance(info.grid, fm.UnstructuredPoints):
            self._plot_cells(axes, points, cells, axes_indices, color)

        axes.scatter(*data_points.T[[ax_1, ax_2]], marker="+", c=color)

        if not isinstance(info.grid, fm.data.StructuredGrid):
            return

        axes_inc = info.grid.axes_increase[[ax_1, ax_2]]
        x_axis = info.grid.axes[ax_1]
        y_axis = info.grid.axes[ax_2]
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

    def _plot_cells(self, axes, points, cells, axes_indices, color):
        ax_1 = axes_indices[0]
        ax_2 = axes_indices[1]
        for nodes in cells:
            for i, node in enumerate(nodes):
                pt1 = points[node]
                pt2 = points[nodes[(i + 1) % len(nodes)]]
                axes.plot(
                    [pt1[ax_1], pt2[ax_1]],
                    [pt1[ax_2], pt2[ax_2]],
                    c=color,
                    lw=0.5,
                )

    def _data_changed(self, _caller, _time):
        self.update()
