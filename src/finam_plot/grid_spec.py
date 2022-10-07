"""Components for plotting grid specifications"""
import matplotlib.pyplot as plt
from finam.core.interfaces import ComponentStatus
from finam.core.sdk import AComponent, CallbackInput
from finam.data import Info
from finam.tools.connect_helper import ConnectHelper


class GridSpecPlot(AComponent):
    """Plots the geometry of grid specifications"""

    def __init__(self):
        super().__init__()
        self._figure = None
        self._connector: ConnectHelper = None
        self._info: Info = None

        self.status = ComponentStatus.CREATED

    def initialize(self):
        super().initialize()

        self.inputs["GridSpec"] = CallbackInput(self._data_changed)
        self._connector = ConnectHelper(self.inputs, self.outputs)

        self.status = ComponentStatus.INITIALIZED

    def connect(self):
        super().connect()
        self.status = self._connector.connect(
            None, exchange_infos={"GridSpec": Info(grid=None, meta={"units": None})}
        )

        info = self._connector.in_infos["GridSpec"]
        if info is not None:
            self._info = info

    def validate(self):
        super().validate()

        self.status = ComponentStatus.VALIDATED

    def update(self):
        super().update()

        if self.status != ComponentStatus.VALIDATED:
            return

        self._figure, axes = plt.subplots()
        axes.set_aspect("equal")

        data_points = self._info.grid.data_points
        points = self._info.grid.points
        cells = self._info.grid.cells

        for nodes in cells:
            for i, node in enumerate(nodes):
                pt1 = node
                pt2 = points[nodes[(i + 1) % len(nodes)]]
                axes.plot([pt1[0], pt2[0]], [pt1[1], pt2[1]], c="0.5", lw=0.5)

        axes.scatter(*data_points.T, marker="+")

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
