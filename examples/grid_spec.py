from datetime import datetime, timedelta

import matplotlib.pyplot as plt
from finam.core.schedule import Composition
from finam.data import Info, UniformGrid
from finam.data.grid_tools import Location
from finam.modules.generators import CallbackGenerator

from finam_plot.grid_spec import GridSpecPlot

if __name__ == "__main__":
    info = Info(grid=UniformGrid((10, 7)), meta={"unit": "source_unit"})
    source = CallbackGenerator(
        callbacks={
            "Output": (
                lambda t: 1,
                info,
            )
        },
        start=datetime(2000, 1, 1),
        step=timedelta(days=1),
    )

    plot = GridSpecPlot()

    comp = Composition([source, plot])
    comp.initialize()

    source.outputs["Output"] >> plot.inputs["GridSpec"]

    comp.run(datetime(2000, 1, 2))

    plt.ion()
    plt.show(block=True)
