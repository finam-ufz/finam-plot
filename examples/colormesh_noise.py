from datetime import datetime, timedelta

import finam as fm
import numpy as np

from finam_plot import ColorMeshPlot

if __name__ == "__main__":
    x = np.linspace(0, 29, 30) + np.random.uniform(-0.4, 0.4, (30,))
    y = np.linspace(0, 19, 20) + np.random.uniform(-0.4, 0.4, (20,))
    grid = fm.RectilinearGrid([x, y])

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
    plot = ColorMeshPlot(limits=(-1, 1))

    comp = fm.Composition([source, trigger, plot])
    comp.initialize()

    source.outputs["Noise"] >> trigger.inputs["In"]
    trigger.outputs["Out"] >> plot.inputs["Image"]

    comp.run(datetime(2001, 1, 1))
