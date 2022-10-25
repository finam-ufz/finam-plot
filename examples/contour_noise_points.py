from datetime import datetime, timedelta

import finam as fm
import numpy as np

from finam_plot import ContourPlot

if __name__ == "__main__":
    grid = fm.UnstructuredPoints(np.random.uniform(0, 50, (500, 2)))

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
    plot = ContourPlot(limits=(-1, 1), triangulate=True)

    comp = fm.Composition([source, trigger, plot])
    comp.initialize()

    source.outputs["Noise"] >> trigger.inputs["In"]
    trigger.outputs["Out"] >> plot.inputs["Grid"]

    comp.run(datetime(2001, 1, 1))
