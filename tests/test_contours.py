import unittest
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
import pint
import pint_xarray
import xarray as xr
from finam.core.schedule import Composition
from finam.data import Info, UniformGrid
from finam.data.grid_spec import UnstructuredGrid, UnstructuredPoints
from finam.data.grid_tools import CellType, Location
from finam.modules.generators import CallbackGenerator

from finam_plot.contour import ContourPlot


class TestContour(unittest.TestCase):
    def test_contour_points(self):
        reg = pint.UnitRegistry(force_ndarray_like=True)

        points = 100
        info_1 = Info(
            grid=UnstructuredPoints(
                np.random.uniform(0, 100, 2 * points).reshape((points, 2))
            ),
            meta={"unit": "source_unit"},
        )
        grid = xr.DataArray(np.zeros(shape=(points,))).pint.quantify(reg.meter)

        for i in range(points):
            grid.data[i] = i * grid.pint.units

        source = CallbackGenerator(
            callbacks={
                "Out": (
                    lambda t: grid,
                    info_1,
                )
            },
            start=datetime(2000, 1, 1),
            step=timedelta(days=1),
        )

        plot = ContourPlot(triangulate=True)

        comp = Composition([source, plot])
        comp.initialize()

        source.outputs["Out"] >> plot.inputs["Grid"]

        comp.run(datetime(2000, 1, 2))

        self.assertEqual(plot._info, info_1)

    def test_contour_tris(self):
        reg = pint.UnitRegistry(force_ndarray_like=True)

        points = [[0, 0], [0, 1], [1, 0], [1, 1]]
        cells = [[0, 1, 2], [1, 2, 3]]
        info_1 = Info(
            grid=UnstructuredGrid(
                points=points,
                cells=cells,
                cell_types=[CellType.TRI.value] * len(cells),
                data_location=Location.POINTS,
            ),
            meta={"unit": "source_unit"},
        )
        grid = xr.DataArray(np.zeros(shape=(len(points),))).pint.quantify(reg.meter)

        for i in range(len(points)):
            grid.data[i] = np.random.uniform(0.0, 1.0, 1) * grid.pint.units

        source = CallbackGenerator(
            callbacks={
                "Out": (
                    lambda t: grid,
                    info_1,
                )
            },
            start=datetime(2000, 1, 1),
            step=timedelta(days=1),
        )

        plot = ContourPlot(fill=True, triangulate=False)

        comp = Composition([source, plot])
        comp.initialize()

        source.outputs["Out"] >> plot.inputs["Grid"]

        comp.run(datetime(2000, 1, 3))

        self.assertEqual(plot._info, info_1)

    def test_contour_quads(self):
        reg = pint.UnitRegistry(force_ndarray_like=True)

        points = [[0, 0], [0, 1], [1, 1], [1, 0]]
        cells = [[0, 1, 2, 3]]
        info_1 = Info(
            grid=UnstructuredGrid(
                points=points,
                cells=cells,
                cell_types=[CellType.QUAD.value] * len(cells),
                data_location=Location.POINTS,
            ),
            meta={"unit": "source_unit"},
        )
        grid = xr.DataArray(np.zeros(shape=(len(points),))).pint.quantify(reg.meter)

        for i in range(len(points)):
            grid.data[i] = np.random.uniform(0.0, 1.0, 1) * grid.pint.units

        source = CallbackGenerator(
            callbacks={
                "Out": (
                    lambda t: grid,
                    info_1,
                )
            },
            start=datetime(2000, 1, 1),
            step=timedelta(days=1),
        )

        plot = ContourPlot(triangulate=True)

        comp = Composition([source, plot])
        comp.initialize()

        source.outputs["Out"] >> plot.inputs["Grid"]

        comp.run(datetime(2000, 1, 2))

        self.assertEqual(plot._info, info_1)
