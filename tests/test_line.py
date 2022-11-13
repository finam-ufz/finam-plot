import unittest
from datetime import datetime, timedelta

import finam as fm
from matplotlib import pyplot

from finam_plot import LinePlot


class TestLine(unittest.TestCase):
    def test_line(self):
        start = datetime(2000, 1, 1)
        grid = fm.UniformGrid((20, 25))

        source_1 = fm.modules.SimplexNoise(
            info=fm.Info(None, grid=grid, units=""),
            frequency=0.05,
            time_frequency=1.0 / (100 * 24 * 3600),
            octaves=3,
            persistence=0.5,
            seed=0,
        )
        source_2 = fm.modules.SimplexNoise(
            info=fm.Info(None, grid=grid, units=""),
            frequency=0.05,
            time_frequency=1.0 / (100 * 24 * 3600),
            octaves=4,
            persistence=0.5,
            seed=1,
        )
        trigger_1 = fm.modules.TimeTrigger(
            start=start,
            step=timedelta(days=10),
            in_info=fm.Info(time=None, grid=None, units=None),
        )
        trigger_2 = fm.modules.TimeTrigger(
            start=start,
            step=timedelta(days=1),
            in_info=fm.Info(time=None, grid=None, units=None),
        )
        plot = LinePlot(["In1", "In2"])

        comp = fm.Composition([source_1, source_2, trigger_1, trigger_2, plot])
        comp.initialize()

        (
            source_1.outputs["Noise"]
            >> fm.adapters.Histogram(lower=-1, upper=1, bins=20)
            >> trigger_1.inputs["In"]
        )
        (
            source_2.outputs["Noise"]
            >> fm.adapters.Histogram(lower=-1, upper=1, bins=20)
            >> trigger_2.inputs["In"]
        )
        trigger_1.outputs["Out"] >> plot.inputs["In1"]
        trigger_2.outputs["Out"] >> plot.inputs["In2"]

        comp.connect()
        comp.run(datetime(2000, 1, 10))

        pyplot.close("all")
