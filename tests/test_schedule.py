import unittest
from datetime import datetime, timedelta

import finam as fm
from matplotlib import pyplot

from finam_plot import SchedulePlot


class TestSchedule(unittest.TestCase):
    def test_schedule(self):
        start = datetime(2000, 1, 1)

        gen1 = fm.modules.CallbackGenerator(
            callbacks={"Out": (lambda t: 0, fm.Info(None, grid=fm.NoGrid()))},
            start=start,
            step=timedelta(days=1),
        )
        gen2 = fm.modules.CallbackGenerator(
            callbacks={"Out": (lambda t: 0, fm.Info(None, grid=fm.NoGrid()))},
            start=start,
            step=timedelta(days=3),
        )

        schedule = SchedulePlot(["Gen1", "Gen2"])

        comp = fm.Composition([gen1, gen2, schedule])
        comp.initialize()

        gen1.outputs["Out"] >> schedule.inputs["Gen1"]
        gen2.outputs["Out"] >> schedule.inputs["Gen2"]

        comp.run(end_time=datetime(2000, 1, 15))

        pyplot.close("all")
