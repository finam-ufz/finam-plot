import datetime as dt

import finam as fm

from finam_plot import TimeSeriesPlot


def run_model():
    start_time = dt.datetime(2000, 1, 1)
    end_time = dt.datetime(2000, 3, 31)

    counter = 0

    info1 = fm.Info(time=None, grid=fm.NoGrid(), units="m")
    data = [
        fm.data.full(0.0, "input", info1),
        fm.data.full(1.0, "input", info1),
    ]

    def gen_data(t):
        nonlocal counter
        d = data[(counter // 2) % 2]
        counter += 1
        return d

    source = fm.components.CallbackGenerator(
        callbacks={
            "Out1": (gen_data, info1.copy()),
            "Out2": (gen_data, info1.copy()),
        },
        start=start_time,
        step=dt.timedelta(days=1),
    )
    plot = TimeSeriesPlot(inputs=["In1", "In2"])

    composition = fm.Composition([source, plot])

    source["Out1"] >> plot["In1"]
    source["Out2"] >> plot["In2"]

    composition.run(end_time=end_time)


if __name__ == "__main__":
    for i in range(1):
        run_model()
