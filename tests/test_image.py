import unittest
from datetime import datetime, timedelta

import finam as fm
import numpy as np
from finam.modules.generators import CallbackGenerator

from finam_plot.image import ImagePlot


class TestImage(unittest.TestCase):
    def test_image_unifform(self):
        info_1 = fm.Info(
            time=None,
            grid=fm.UniformGrid(
                dims=(15, 12),
                data_location=fm.Location.POINTS,
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

        plot = ImagePlot(axes=(0, 1))

        comp = fm.Composition([source, plot])
        comp.initialize()

        source.outputs["Out"] >> plot.inputs["Image"]

        comp.run(datetime(2000, 1, 5))

        self.assertEqual(plot._info, info_1)
