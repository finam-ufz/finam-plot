from datetime import datetime, timedelta

import finam as fm
import matplotlib.pyplot as plt
import numpy as np

from finam_plot import ContourPlot

if __name__ == "__main__":
    grid = fm.UnstructuredPoints(np.random.uniform(0, 50, (500, 2)))

    source = fm.components.SimplexNoise(
        info=fm.Info(None, grid=grid, units=""),
        frequency=0.05,
        time_frequency=1.0 / (30 * 24 * 3600),
        octaves=3,
        persistence=0.5,
    )
    trigger = fm.components.TimeTrigger(
        start=datetime(2000, 1, 1),
        step=timedelta(days=1),
        in_info=fm.Info(time=None, grid=None, units=None),
    )
    plot = ContourPlot(title="Simplex noise", triangulate=True, vmin=-1, vmax=1)

    comp = fm.Composition([source, trigger, plot])

    source.outputs["Noise"] >> trigger.inputs["In"]
    trigger.outputs["Out"] >> plot.inputs["Grid"]

    comp.run(end_time=datetime(2001, 1, 1))

    plt.ion()
    plt.show(block=True)
