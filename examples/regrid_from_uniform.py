import finam as fm
import matplotlib.pyplot as plt
import numpy as np

from finam_plot import ContourPlot, GridSpecPlot, ImagePlot

if __name__ == "__main__":
    in_grid = fm.UniformGrid((21, 17))

    uniform_grid = fm.UniformGrid((51, 41), spacing=(0.4, 0.4))

    px = np.random.uniform(0, 20, 500)
    py = np.random.uniform(0, 16, 500)
    unstructured_grid = fm.UnstructuredPoints(list(zip(px, py)))

    source = fm.modules.StaticSimplexNoise(
        info=fm.Info(None, grid=in_grid, units=""),
        frequency=0.05,
        octaves=3,
        persistence=0.5,
    )
    plot_orig = ImagePlot(title="Original", vmin=-1, vmax=1, cmap="hsv")
    plot_unif = ImagePlot(title="UniformGrid", vmin=-1, vmax=1, cmap="hsv")
    plot_points = ContourPlot(
        title="UnstructuredPoints", triangulate=True, vmin=-1, vmax=1, cmap="hsv"
    )

    specs = GridSpecPlot(["Unif", "Orig", "Points"], title="Grid specifications")

    regrid_unif = fm.adapters.RegridLinear(
        out_grid=uniform_grid, fill_with_nearest=True
    )
    regrid_points = fm.adapters.RegridLinear(
        out_grid=unstructured_grid, fill_with_nearest=True
    )

    comp = fm.Composition([source, plot_orig, plot_unif, plot_points, specs])
    comp.initialize()

    source.outputs["Noise"] >> plot_orig.inputs["Grid"]
    (source.outputs["Noise"] >> regrid_unif >> plot_unif.inputs["Grid"])
    (source.outputs["Noise"] >> regrid_points >> plot_points.inputs["Grid"])

    source["Noise"] >> specs["Orig"]
    regrid_unif >> specs["Unif"]
    regrid_points >> specs["Points"]

    comp.run()

    plt.ion()
    plt.show(block=True)
