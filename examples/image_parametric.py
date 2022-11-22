import math
from datetime import datetime, timedelta

import finam as fm
import matplotlib.pyplot as plt

from finam_plot import ImagePlot

if __name__ == "__main__":
    start = datetime(2000, 1, 1)
    grid = fm.UniformGrid((50, 40), order="C")

    def func(t, x, y):
        days = (t - start).days
        xy_func = math.sin(0.4 * (x - days)) * math.sin(0.4 * y)
        t_func = math.sin(0.1 * days)
        return xy_func * t_func

    source = fm.modules.ParametricGrid(
        info=fm.Info(None, grid=grid, units=""),
        func=func,
    )
    trigger = fm.modules.TimeTrigger(
        start=start,
        step=timedelta(days=1),
        in_info=fm.Info(time=None, grid=None, units=None),
    )
    plot = ImagePlot(
        title="Parametric grid",
        pos=(0.5, 0.5),
        size=(400, 300),
        vmin=-1,
        vmax=1,
    )

    comp = fm.Composition([source, trigger, plot])
    comp.initialize()

    source.outputs["Grid"] >> trigger.inputs["In"]
    trigger.outputs["Out"] >> plot.inputs["Grid"]

    comp.run(datetime(2001, 1, 1))

    plt.ion()
    plt.show(block=True)
