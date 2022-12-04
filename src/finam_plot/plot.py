"""Base classes for plots"""
from abc import ABC

import finam as fm

from .tools import create_figure


class PlotBase(fm.Component, ABC):
    """Base class for push-based plots"""

    def __init__(
        self, title=None, pos=None, size=None, update_interval=1, **plot_kwargs
    ):
        fm.Component.__init__(self)
        self.figure = None
        self.axes = None

        self._title = title
        self._bounds = (pos, size)
        self._update_interval = update_interval
        self._update_counter = 0

        self.plot_kwargs = plot_kwargs

    def _validate(self):
        pass

    def _update(self):
        pass

    def _finalize(self):
        pass

    def create_figure(self):
        """Creates a figure with the plot's title and size."""
        self.figure, self.axes = create_figure(self._bounds)
        self.figure.canvas.manager.set_window_title(self._title or "FINAM")
        self.axes.set_title(self._title)

    def should_repaint(self):
        """Returns whether the plot should repaint, based on it's undate interval."""
        rep = self._update_counter % self._update_interval == 0
        self._update_counter += 1
        return rep

    def repaint(self, relim=False):
        """Repaints the plot window."""
        if relim:
            self.axes.relim()
            self.axes.autoscale_view(True, True, True)

        self.figure.canvas.draw_idle()
        self.figure.canvas.flush_events()
