from datetime import datetime, timedelta

import finam as fm
import matplotlib.pyplot as plt

from finam_plot import SchedulePlot


def transform(inputs, _time):
    return {"Out": fm.data.strip_data(inputs["In"]) * 2.0}


if __name__ == "__main__":
    time = datetime(2000, 1, 1)
    info = fm.Info(None, grid=fm.NoGrid())

    source_1 = fm.modules.CallbackGenerator(
        callbacks={"Out": (lambda t: 0, info)},
        start=time,
        step=timedelta(days=1),
    )
    source_2 = fm.modules.CallbackComponent(
        inputs={"In": info},
        outputs={"Out": info},
        callback=transform,
        start=time,
        step=timedelta(days=5),
    )
    source_3 = fm.modules.CallbackComponent(
        inputs={"In": info},
        outputs={"Out": info},
        callback=transform,
        start=time,
        step=timedelta(days=30),
    )
    plot = SchedulePlot(["1d", "5d", "30d"])

    comp = fm.Composition([source_1, source_2, source_3, plot])
    comp.initialize()

    source_1.outputs["Out"] >> source_2.inputs["In"]
    source_2.outputs["Out"] >> source_3.inputs["In"]

    source_1.outputs["Out"] >> plot.inputs["1d"]
    source_2.outputs["Out"] >> plot.inputs["5d"]
    source_3.outputs["Out"] >> plot.inputs["30d"]

    comp.run(datetime(2001, 1, 1))

    plt.ion()
    plt.show(block=True)
