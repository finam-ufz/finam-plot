"""
FINAM components for plotting spatial and temporal data.

.. toctree::
   :hidden:

   self

Grid and mesh plots
===================

.. autosummary::
   :toctree: generated
   :caption: Grid and mesh plots

    ColorMeshPlot
    ContourPlot
    GridSpecPlot
    ImagePlot

Point and line plots
====================

.. autosummary::
   :toctree: generated
   :caption: Point and line plots

    LinePlot
    SchedulePlot
    StepTimeSeriesPlot
    TimeSeriesPlot

"""
from .colormesh import ColorMeshPlot
from .contour import ContourPlot
from .grid_spec import GridSpecPlot
from .image import ImagePlot
from .line import LinePlot
from .schedule import SchedulePlot
from .time_series import StepTimeSeriesPlot, TimeSeriesPlot

try:
    from ._version import __version__
except ModuleNotFoundError:  # pragma: no cover
    # package is not installed
    __version__ = "0.0.0.dev0"

__all__ = [
    "ColorMeshPlot",
    "ContourPlot",
    "GridSpecPlot",
    "ImagePlot",
    "LinePlot",
    "SchedulePlot",
    "StepTimeSeriesPlot",
    "TimeSeriesPlot",
]
