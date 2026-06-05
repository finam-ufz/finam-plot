# Release notes

## [v0.3.0]

### Features

* compatible with FINAM v1

### Breaking changes

* migrate examples and tests from `fm.modules` to `fm.components` for FINAM v1

### Documentation

* update installation instructions for the PyPI package

### Bugfixes

* fix ydata setting for newer mpl versions
* Contour: fill masked data with nan for unstructured plot
* time-series: fix units string gen
* fix figure positioning with non-Tk GUI backends


## [v0.2.0]

### Features

* Grid plots accept static data (!17)
* Plot window title can be configured via constructor argument (!17)
* Grid plots show the current time (!17)
* New `XyPlot` for scatter plots and instant line plots (i.e. no time series) (!21)
* Configurable plot window size and position (!24)
* All grid plots have color bar legends (!25)
* Time series plot shows series units in the legend (!28)
* In time series plots, units can be forced to be converted to compatible units (!31)

### Documentation

* Docs are now styled like the FINAM main documentation (!18)

### Bugfixes

* Plots windows are no longer brought to front on every redraw (!23)
* Fix for transposed grid plots (!30, !37)

### Other

* Adapted to new scheduling algorithm in FINAM v0.4.0 (!16)
* Adapted to handle starting time treatment in FINAM v0.4.0 (!32)

## [v0.1.0]

* initial release of finam_plot

[unpublished]: https://git.ufz.de/FINAM/finam-plot/-/compare/v0.3.0...main
[v0.3.0]: https://git.ufz.de/FINAM/finam-plot/-/compare/v0.2.0...v0.3.0
[v0.2.0]: https://git.ufz.de/FINAM/finam-plot/-/compare/v0.1.0...v0.2.0
[v0.1.0]: https://git.ufz.de/FINAM/finam-plot/-/commits/v0.1.0
