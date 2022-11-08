import finam as fm
import matplotlib.pyplot as plt
import numpy as np

from finam_plot import ContourPlot, ImagePlot

if __name__ == "__main__":
    in_grid = fm.UniformGrid((30, 20))

    uniform_grid = fm.UniformGrid((60, 40), spacing=(0.5, 0.5))

    px = np.random.uniform(0, 30, 1000)
    py = np.random.uniform(0, 20, 1000)
    unstructured_grid = fm.UnstructuredPoints(list(zip(px, py)))

    source = fm.modules.StaticSimplexNoise(
        info=fm.Info(None, grid=in_grid, units=""),
        frequency=0.05,
        octaves=3,
        persistence=0.5,
    )
    plot_orig = ImagePlot(vmin=-1, vmax=1, cmap="hsv")
    plot_unif = ImagePlot(vmin=-1, vmax=1, cmap="hsv")
    plot_points = ContourPlot(triangulate=True, vmin=-1, vmax=1, cmap="hsv")

    comp = fm.Composition([source, plot_orig, plot_unif, plot_points])
    comp.initialize()

    source.outputs["Noise"] >> plot_orig.inputs["Grid"]
    (
        source.outputs["Noise"]
        >> fm.adapters.RegridLinear(out_grid=uniform_grid, fill_with_nearest=True)
        >> plot_unif.inputs["Grid"]
    )
    (
        source.outputs["Noise"]
        >> fm.adapters.RegridLinear(out_grid=unstructured_grid, fill_with_nearest=True)
        >> plot_points.inputs["Grid"]
    )

    comp.run()

    plt.ion()
    plt.show(block=True)
