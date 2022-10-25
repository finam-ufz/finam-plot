import unittest
from datetime import datetime, timedelta

import finam as fm
from matplotlib import pyplot

from finam_plot import StepTimeSeriesPlot, TimeSeriesPlot


class TestStepTimeSeries(unittest.TestCase):
    def test_step_time_series(self):
        start = datetime(2000, 1, 1)

        gen1 = fm.modules.CallbackGenerator(
            callbacks={"Out": (lambda t: 0, fm.Info(None, grid=fm.NoGrid()))},
            start=start,
            step=timedelta(days=1),
        )
        gen2 = fm.modules.CallbackGenerator(
            callbacks={
                "Out": (lambda t: (t - start).days, fm.Info(None, grid=fm.NoGrid()))
            },
            start=start,
            step=timedelta(days=3),
        )

        series = StepTimeSeriesPlot(
            ["Gen1", "Gen2"], start=start, step=timedelta(days=3)
        )

        comp = fm.Composition([gen1, gen2, series])
        comp.initialize()

        gen1.outputs["Out"] >> series.inputs["Gen1"]
        gen2.outputs["Out"] >> series.inputs["Gen2"]

        comp.run(t_max=datetime(2000, 1, 15))

        pyplot.close("all")

    def test_time_fail(self):
        with self.assertRaises(ValueError):
            _series = StepTimeSeriesPlot(
                ["Gen1", "Gen2"], start=0, step=timedelta(days=3)
            )
        with self.assertRaises(ValueError):
            _series = StepTimeSeriesPlot(
                ["Gen1", "Gen2"], start=datetime(2000, 1, 1), step=0
            )


class TestPushTimeSeries(unittest.TestCase):
    def test_push_time_series(self):
        start = datetime(2000, 1, 1)

        gen1 = fm.modules.CallbackGenerator(
            callbacks={"Out": (lambda t: 0, fm.Info(None, grid=fm.NoGrid()))},
            start=start,
            step=timedelta(days=1),
        )
        gen2 = fm.modules.CallbackGenerator(
            callbacks={
                "Out": (lambda t: (t - start).days, fm.Info(None, grid=fm.NoGrid()))
            },
            start=start,
            step=timedelta(days=3),
        )

        series = TimeSeriesPlot(["Gen1", "Gen2"], colors=["red", "black"], marker="o")

        comp = fm.Composition([gen1, gen2, series])
        comp.initialize()

        gen1.outputs["Out"] >> series.inputs["Gen1"]
        gen2.outputs["Out"] >> series.inputs["Gen2"]

        comp.run(t_max=datetime(2000, 1, 15))

        pyplot.close("all")
