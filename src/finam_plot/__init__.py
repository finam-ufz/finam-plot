"""
FINAM components for plotting spatial and temporal data.

.. toctree::
   :hidden:

   self

Components
==========

.. autosummary::
   :toctree: generated
   :caption: Components

    ColorMeshPlot
    ContourPlot
    GridSpecPlot
    ImagePlot

.. autosummary::
   :toctree: generated
   :caption: Adapters

"""
from .colormesh import ColorMeshPlot
from .contour import ContourPlot
from .grid_spec import GridSpecPlot
from .image import ImagePlot

__all__ = [
    "ColorMeshPlot",
    "ContourPlot",
    "GridSpecPlot",
    "ImagePlot",
]
