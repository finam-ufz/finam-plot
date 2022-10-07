from datetime import datetime, timedelta

import matplotlib.pyplot as plt
from finam.core.schedule import Composition
from finam.data import Info, UniformGrid
from finam.data.grid_tools import Location
from finam.modules.generators import CallbackGenerator

from finam_plot.grid_spec import GridSpecPlot

if __name__ == "__main__":
    info_1 = Info(grid=UniformGrid((10, 7)), meta={"unit": "source_unit"})
    info_2 = Info(
        grid=UniformGrid(
            (6, 4),
            spacing=(1.345, 1.345),
            origin=(1.345, 1.345),
            axes_increase=[True, False],
        ),
        meta={"unit": "source_unit"},
    )
    source = CallbackGenerator(
        callbacks={
            "Out1": (
                lambda t: 1,
                info_1,
            ),
            "Out2": (
                lambda t: 1,
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
