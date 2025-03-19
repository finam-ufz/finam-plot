import unittest
from datetime import datetime, timedelta

import finam as fm
import numpy as np
from finam.modules import CallbackGenerator
from matplotlib import pyplot

from finam_plot import ImagePlot


class TestImage(unittest.TestCase):
    def test_image_uniform(self):
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

        plot = ImagePlot(pos=(0.2, 0.2), size=(0.33, 0.4), vmin=0, vmax=1)

        comp = fm.Composition([source, plot])

        source.outputs["Out"] >> plot.inputs["Grid"]

        comp.run(end_time=datetime(2000, 1, 5))

        self.assertEqual(plot._info, info_1)

        pyplot.close("all")

    def test_image_masked(self):
        info_1 = fm.Info(
            time=None,
            grid=fm.UniformGrid(
                dims=(15, 12),
                data_location=fm.Location.POINTS,
            ),
            units="m",
        )

        def generate_data(grid):
            arr = np.reshape(
                np.random.random(info_1.grid.data_size),
                newshape=info_1.grid.data_shape,
                order=grid.order,
            )
            data = fm.UNITS.Quantity(
                np.ma.masked_where(arr < 0.2, arr),
                fm.UNITS.meter,
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

        plot = ImagePlot(pos=(0.2, 0.2), size=(0.33, 0.4), vmin=0, vmax=1)

        comp = fm.Composition([source, plot])

        source.outputs["Out"] >> plot.inputs["Grid"]

        comp.run(end_time=datetime(2000, 1, 5))

        self.assertEqual(plot._info, info_1)

        pyplot.close("all")
