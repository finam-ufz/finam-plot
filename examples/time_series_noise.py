from datetime import datetime, timedelta

import finam as fm
import matplotlib.pyplot as plt

from finam_plot import TimeSeriesPlot

if __name__ == "__main__":
    grid = fm.NoGrid()

    source_1 = fm.modules.SimplexNoise(
        info=fm.Info(None, grid=grid, units="m"),
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
        start=datetime(2000, 1, 1),
        step=timedelta(days=10),
        in_info=fm.Info(time=None, grid=None, units=None),
    )
    trigger_2 = fm.modules.TimeTrigger(
        start=datetime(2000, 1, 1),
        step=timedelta(days=1),
        in_info=fm.Info(time=None, grid=None, units=None),
    )
    plot = TimeSeriesPlot(["In1", "In2"])

    comp = fm.Composition([source_1, source_2, trigger_1, trigger_2, plot])

    source_1.outputs["Noise"] >> trigger_1.inputs["In"]
    source_2.outputs["Noise"] >> trigger_2.inputs["In"]
    trigger_1.outputs["Out"] >> plot.inputs["In1"]
    trigger_2.outputs["Out"] >> plot.inputs["In2"]

    comp.run(end_time=datetime(2001, 1, 1))

    plt.ion()
    plt.show(block=True)
