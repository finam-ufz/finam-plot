from datetime import datetime, timedelta

import finam as fm
import matplotlib.pyplot as plt

from finam_plot import XyPlot

if __name__ == "__main__":
    grid = fm.UniformGrid((30, 20), order="C")

    source = fm.modules.SimplexNoise(
        info=fm.Info(None, grid=grid, units=""),
        frequency=0.05,
        time_frequency=1.0 / (30 * 24 * 3600),
        octaves=3,
        persistence=0.5,
    )
    trigger = fm.modules.TimeTrigger(
        start=datetime(2000, 1, 1),
        step=timedelta(days=1),
        in_info=fm.Info(time=None, grid=None, units=None),
    )
    plot = XyPlot(
        title="Histogram",
        inputs=["Hist"],
        pos=(0.5, 0.5),
        size=(400, 300),
    )

    comp = fm.Composition([source, trigger, plot])
    comp.initialize()

    (
        source.outputs["Noise"]
        >> fm.adapters.Histogram(lower=-1, upper=1, bins=50)
        >> trigger.inputs["In"]
    )
    trigger.outputs["Out"] >> plot.inputs["Hist"]

    comp.run(end_time=datetime(2001, 1, 1))

    plt.ion()
    plt.show(block=True)
