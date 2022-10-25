import unittest
from datetime import datetime, timedelta

import finam as fm
import numpy as np
from finam.modules.generators import CallbackGenerator

from finam_plot.colormesh import ColorMeshPlot


class TestColorMesh(unittest.TestCase):
    def test_colormesh_rectilinear(self):
        info_1 = fm.Info(
            time=None,
            grid=fm.RectilinearGrid(
                [
                    np.asarray([0, 1, 2, 4, 7, 9, 10, 11, 12]),
                    np.asarray([1, 2, 4, 6, 7, 8, 9, 12, 15, 16, 17]),
                ],
                data_location=fm.Location.CELLS,
            ),
            units="m",
        )

        def generate_data(grid):
            data = (
                np.reshape(
                    np.random.random(info_1.grid.data_size),
                    newshape=info_1.grid.data_shape,
                    order=grid.order,
                )
                * fm.UNITS.meter
            )
            data[0, 0] = 2 * fm.UNITS.meter
            return data

        source = CallbackGenerator(
            callbacks={
                "Out": (
                    lambda t: generate_data(info_1.grid),
                    info_1,
                )
            },
            start=datetime(2000, 1, 1),
            step=timedelta(days=1),
        )

        plot = ColorMeshPlot(axes=(0, 1))

        comp = fm.Composition([source, plot])
        comp.initialize()

        source.outputs["Out"] >> plot.inputs["Image"]

        comp.run(datetime(2000, 1, 5))

        self.assertEqual(plot._info, info_1)
