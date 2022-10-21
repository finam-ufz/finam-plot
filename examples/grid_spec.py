from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import numpy as np
from finam import UNITS, Composition, Info, UniformGrid
from finam.modules.generators import CallbackGenerator

from finam_plot.grid_spec import GridSpecPlot

if __name__ == "__main__":
    info_1 = Info(time=None, grid=UniformGrid((10, 7)), units="m")
    info_2 = Info(
        time=None,
        grid=UniformGrid(
            (6, 4),
            spacing=(1.345, 1.345),
            origin=(1.345, 1.345),
            axes_increase=[True, False],
        ),
        units="m",
    )
    grid_1 = (
        np.zeros(shape=info_1.grid.data_shape, order=info_1.grid.order) * UNITS.meter
    )
    grid_2 = (
        np.zeros(shape=info_2.grid.data_shape, order=info_2.grid.order) * UNITS.meter
    )
    source = CallbackGenerator(
        callbacks={
            "Out1": (
                lambda t: grid_1,
                info_1,
            ),
            "Out2": (
                lambda t: grid_2,
                info_2,
            ),
        },
        start=datetime(2000, 1, 1),
        step=timedelta(days=1),
    )

    plot = GridSpecPlot(["In1", "In2"], axes=("x", "y"), colors=["black", "red"])

    comp = Composition([source, plot])
    comp.initialize()

    source.outputs["Out1"] >> plot.inputs["In1"]
    source.outputs["Out2"] >> plot.inputs["In2"]

    comp.run(datetime(2000, 1, 2))

    plt.ion()
    plt.show(block=True)
