from datetime import datetime, timedelta

import finam as fm
import matplotlib.pyplot as plt
import numpy as np

from finam_plot import ColorMeshPlot

if __name__ == "__main__":
    x = np.linspace(0, 29, 30) + np.random.uniform(-0.4, 0.4, (30,))
    y = np.linspace(0, 19, 20) + np.random.uniform(-0.4, 0.4, (20,))
    grid = fm.RectilinearGrid([x, y], order="C")

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
    plot = ColorMeshPlot(title="Simplex noise", vmin=-1, vmax=1, cmap="hsv")

    comp = fm.Composition([source, trigger, plot])

    source.outputs["Noise"] >> trigger.inputs["In"]
    trigger.outputs["Out"] >> plot.inputs["Grid"]

    comp.run(end_time=datetime(2001, 1, 1))

    plt.ion()
    plt.show(block=True)
