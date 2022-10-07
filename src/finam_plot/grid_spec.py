"""Components for plotting grid specifications"""
import matplotlib.pyplot as plt
from finam.core.interfaces import ComponentStatus
from finam.core.sdk import AComponent, CallbackInput
from finam.data import Info
from finam.tools.connect_helper import ConnectHelper


class GridSpecPlot(AComponent):
    """Plots the geometry of grid specifications"""

    def __init__(self, inputs):
        super().__init__()
        self._figure = None
        self._connector: ConnectHelper = None
        self._input_colors = inputs
        self._infos = {name: None for name, _col in self._input_colors.items()}

        self.drawn = False

        self.status = ComponentStatus.CREATED

    def initialize(self):
        super().initialize()

        for name, _col in self._input_colors.items():
            self.inputs[name] = CallbackInput(self._data_changed)

        self._connector = ConnectHelper(self.inputs, self.outputs)

        self.status = ComponentStatus.INITIALIZED

    def connect(self):
        super().connect()

        exchange_infos = {}
        for name, val in self._connector.in_infos.items():
            if val is None:
                exchange_infos[name] = Info(grid=None, meta={"units": None})
        self.status = self._connector.connect(None, exchange_infos=exchange_infos)

        for name, val in self._connector.in_infos.items():
            if val is not None:
                self._infos[name] = val

    def validate(self):
        super().validate()

        self.status = ComponentStatus.VALIDATED

    def update(self):
        super().update()

        if self.drawn or self.status != ComponentStatus.VALIDATED:
            return

        self.drawn = True

        self._figure, axes = plt.subplots()
        axes.set_aspect("equal")

        for name, info in self._infos.items():
            data_points = info.grid.data_points
            points = info.grid.points
            cells = info.grid.cells

            color = self._input_colors[name]

            for nodes in cells:
                for i, node in enumerate(nodes):
                    pt1 = points[node]
                    pt2 = points[nodes[(i + 1) % len(nodes)]]
                    axes.plot([pt1[0], pt2[0]], [pt1[1], pt2[1]], c=color, lw=0.5)

            axes.scatter(*data_points.T, marker="+", c=color)

        self._figure.show()
        self._figure.tight_layout()
        self._figure.canvas.draw()
        self._figure.canvas.flush_events()

        self.status = ComponentStatus.UPDATED

    def finalize(self):
        super().finalize()

        self.status = ComponentStatus.FINALIZED

    def _data_changed(self, _caller, _time):
        self.update()
