import unittest
from datetime import datetime, timedelta

import finam as fm
import numpy as np
from matplotlib import pyplot
from matplotlib.tri import Triangulation

from finam_plot.contour import ContourPlot


class TestContour(unittest.TestCase):
    def test_contour_points(self):
        points = 100
        info_1 = fm.Info(
            time=None,
            grid=fm.UnstructuredPoints(
                np.random.uniform(0, 100, 2 * points).reshape((points, 2))
            ),
            units="m",
        )
        grid = np.zeros(shape=(points,)) * fm.UNITS.meter

        for i in range(points):
            grid[i] = i * fm.UNITS.meter

        source = fm.modules.CallbackGenerator(
            callbacks={
                "Out": (
                    lambda t: grid.copy(),
                    info_1,
                )
            },
            start=datetime(2000, 1, 1),
            step=timedelta(days=1),
        )

        plot = ContourPlot(triangulate=True, cmap="hsv")

        comp = fm.Composition([source, plot])
        comp.initialize()

        source.outputs["Out"] >> plot.inputs["Grid"]

        comp.run(end_time=datetime(2000, 1, 2))

        self.assertEqual(plot._info, info_1)

        pyplot.close("all")

    def test_contour_tris_points(self):
        points = [[0, 0], [0, 1], [1, 0], [1, 1]]
        cells = [[0, 1, 2], [1, 2, 3]]
        info_1 = fm.Info(
            time=None,
            grid=fm.UnstructuredGrid(
                points=points,
                cells=cells,
                cell_types=[fm.CellType.TRI.value] * len(cells),
                data_location=fm.Location.POINTS,
            ),
            units="m",
        )
        grid = np.zeros(shape=(len(points),)) * fm.UNITS.meter

        for i in range(len(points)):
            grid[i] = np.random.uniform(0.0, 1.0, 1) * fm.UNITS.meter

        source = fm.modules.CallbackGenerator(
            callbacks={
                "Out": (
                    lambda t: grid.copy(),
                    info_1,
                )
            },
            start=datetime(2000, 1, 1),
            step=timedelta(days=1),
        )

        plot = ContourPlot(fill=True, triangulate=False)

        comp = fm.Composition([source, plot])
        comp.initialize()

        source.outputs["Out"] >> plot.inputs["Grid"]

        comp.run(end_time=datetime(2000, 1, 3))

        self.assertEqual(plot._info, info_1)

        pyplot.close("all")

    def test_contour_tris_cells(self):
        num_points = 100
        points = np.random.uniform(0, 100, 2 * num_points).reshape((num_points, 2))
        tris = Triangulation(*points.T)
        cells = tris.get_masked_triangles()
        info_1 = fm.Info(
            time=None,
            grid=fm.UnstructuredGrid(
                points=points,
                cells=cells,
                cell_types=[fm.CellType.TRI.value] * len(cells),
                data_location=fm.Location.CELLS,
            ),
            units="m",
        )
        grid = np.zeros(shape=(len(cells),)) * fm.UNITS.meter

        def generate_data(grid):
            for i in range(len(cells)):
                grid[i] = np.random.uniform(0.0, 1.0, 1) * fm.UNITS.meter
            return grid

        source = fm.modules.CallbackGenerator(
            callbacks={
                "Out": (
                    lambda t: generate_data(grid).copy(),
                    info_1,
                )
            },
            start=datetime(2000, 1, 1),
            step=timedelta(days=1),
        )

        plot = ContourPlot(fill=True, triangulate=False)

        comp = fm.Composition([source, plot])
        comp.initialize()

        source.outputs["Out"] >> plot.inputs["Grid"]

        comp.run(end_time=datetime(2000, 1, 10))

        self.assertEqual(plot._info, info_1)

        pyplot.close("all")

    def test_contour_quads(self):
        points = [[0, 0], [0, 1], [1, 1], [1, 0]]
        cells = [[0, 1, 2, 3]]
        info_1 = fm.Info(
            time=None,
            grid=fm.UnstructuredGrid(
                points=points,
                cells=cells,
                cell_types=[fm.CellType.QUAD.value] * len(cells),
                data_location=fm.Location.POINTS,
            ),
            units="m",
        )
        grid = np.zeros(shape=(len(points),)) * fm.UNITS.meter

        for i in range(len(points)):
            grid[i] = np.random.uniform(0.0, 1.0, 1) * fm.UNITS.meter

        source = fm.modules.CallbackGenerator(
            callbacks={
                "Out": (
                    lambda t: grid.copy(),
                    info_1,
                )
            },
            start=datetime(2000, 1, 1),
            step=timedelta(days=1),
        )

        plot = ContourPlot(triangulate=True)

        comp = fm.Composition([source, plot])
        comp.initialize()

        source.outputs["Out"] >> plot.inputs["Grid"]

        comp.run(end_time=datetime(2000, 1, 2))

        self.assertEqual(plot._info, info_1)

        pyplot.close("all")

    def test_contour_rectilinear(self):
        info_1 = fm.Info(
            time=None,
            grid=fm.RectilinearGrid(
                axes=[
                    np.array([0, 1, 3, 6, 9, 10, 11, 12]),
                    np.array([2, 3, 4, 7, 8, 9, 10]),
                ],
                data_location=fm.Location.POINTS,
            ),
            units="m",
        )
        grid = (
            np.zeros(shape=info_1.grid.data_shape, order=info_1.grid.order)
            * fm.UNITS.meter
        )

        def generate_data(grid):
            for i in range(len(info_1.grid.axes[0])):
                for j in range(len(info_1.grid.axes[1])):
                    grid[i, j] = np.random.uniform(0.0, 1.0, 1) * fm.UNITS.meter
            return grid

        source = fm.modules.CallbackGenerator(
            callbacks={
                "Out": (
                    lambda t: generate_data(grid).copy(),
                    info_1,
                )
            },
            start=datetime(2000, 1, 1),
            step=timedelta(days=1),
        )

        plot = ContourPlot(triangulate=True)

        comp = fm.Composition([source, plot])
        comp.initialize()

        source.outputs["Out"] >> plot.inputs["Grid"]

        comp.run(end_time=datetime(2000, 1, 5))

        self.assertEqual(plot._info, info_1)

        pyplot.close("all")

    def test_contour_lines(self):
        info_1 = fm.Info(
            time=None,
            grid=fm.RectilinearGrid(
                axes=[
                    np.array([0, 1, 3, 6, 9, 10, 11, 12]),
                    np.array([2, 3, 4, 7, 8, 9, 10]),
                ],
                data_location=fm.Location.POINTS,
            ),
            units="m",
        )
        grid = (
            np.zeros(shape=info_1.grid.data_shape, order=info_1.grid.order)
            * fm.UNITS.meter
        )

        def generate_data(grid):
            for i in range(len(info_1.grid.axes[0])):
                for j in range(len(info_1.grid.axes[1])):
                    grid[i, j] = np.random.uniform(0.0, 1.0, 1) * fm.UNITS.meter
            return grid

        source = fm.modules.CallbackGenerator(
            callbacks={
                "Out": (
                    lambda t: generate_data(grid).copy(),
                    info_1,
                )
            },
            start=datetime(2000, 1, 1),
            step=timedelta(days=1),
        )

        plot = ContourPlot(fill=False, triangulate=True)

        comp = fm.Composition([source, plot])
        comp.initialize()

        source.outputs["Out"] >> plot.inputs["Grid"]

        comp.run(end_time=datetime(2000, 1, 5))

        self.assertEqual(plot._info, info_1)

        pyplot.close("all")
