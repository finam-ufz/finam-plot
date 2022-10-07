import unittest
from datetime import datetime, timedelta

from finam.core.schedule import Composition
from finam.data import Info, UniformGrid
from finam.modules.generators import CallbackGenerator

from finam_plot.grid_spec import GridSpecPlot


class TestGridSpec(unittest.TestCase):
    def test_grid_spec(self):
        info_1 = Info(grid=UniformGrid((10, 7)), meta={"unit": "source_unit"})
        info_2 = Info(
            grid=UniformGrid((6, 4), spacing=(1.5, 1.5, 1.5)),
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

        plot = GridSpecPlot(["In1", "In2"], axes=("y", "x"), colors=["black", "blue"])

        comp = Composition([source, plot])
        comp.initialize()

        source.outputs["Out1"] >> plot.inputs["In1"]
        source.outputs["Out2"] >> plot.inputs["In2"]

        comp.run(datetime(2000, 1, 2))

        self.assertEqual(plot._infos, {"In1": info_1, "In2": info_2})
