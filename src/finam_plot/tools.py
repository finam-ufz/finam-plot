"""Tool functions."""
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from mpl_toolkits.axes_grid1 import make_axes_locatable


def create_colorbar(figure, axes, mappable):
    """Add a colorbar by creating a new plot axes"""
    divider = make_axes_locatable(axes)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    mappable = ScalarMappable(norm=mappable.norm, cmap=mappable.cmap)
    figure.colorbar(mappable, cax=cax, orientation="vertical")


def create_figure(bounds):
    """Creates a figure and plot axes"""
    figure, plot_ax = plt.subplots()
    pos, size = convert_bounds(bounds)
    move_figure(figure, pos)

    if size is not None:
        figure.set_size_inches(*size)

    return figure, plot_ax


def convert_bounds(bounds):
    """Convert position and size in pixels or percentage to coordinates in pixels"""
    return convert_pos(bounds[0]), convert_size(bounds[1])


def convert_pos(position):
    """Convert a position in pixels or percentage to coordinates in pixels"""
    if position is None:
        return None

    window = plt.get_current_fig_manager().window
    screen_x, screen_y = window.wm_maxsize()

    return (
        position[0] if isinstance(position[0], int) else int(position[0] * screen_x),
        position[1] if isinstance(position[1], int) else int(position[1] * screen_y),
    )


def convert_size(position):
    """Convert a size in pixels or percentage to coordinates in inches"""
    if position is None:
        return None

    window = plt.get_current_fig_manager().window
    dpi = window.winfo_fpixels("1i")
    scale = dpi / 96

    screen_x, screen_y = window.wm_maxsize()
    screen_x /= scale
    screen_y /= scale

    px = 1 / plt.rcParams["figure.dpi"]

    pos = (
        position[0] if isinstance(position[0], int) else int(position[0] * screen_x),
        position[1] if isinstance(position[1], int) else int(position[1] * screen_y),
    )

    return (
        pos[0] * px,
        pos[1] * px,
    )


def move_figure(f, pos):
    """Move a figure to a position in pixels."""
    if pos is None:
        return

    backend = matplotlib.get_backend()
    if backend == "TkAgg":
        f.canvas.manager.window.wm_geometry(f"+{pos[0]}+{pos[1]}")
    elif backend == "WXAgg":
        f.canvas.manager.window.SetPosition(pos)
    else:
        # This works for QT and GTK
        # You can also use window.setGeometry
        f.canvas.manager.window.move(*pos)
