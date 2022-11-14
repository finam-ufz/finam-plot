"""Tool functions."""
import matplotlib
import matplotlib.pyplot as plt


def convert_pos(position):
    """Convert a position in pixels of percentage to coordinates in pixels"""
    if position is None:
        return None

    window = plt.get_current_fig_manager().window
    dpi = window.winfo_fpixels("1i")
    scale = dpi / 96

    screen_x, screen_y = window.wm_maxsize()
    screen_x /= scale
    screen_y /= scale

    return (
        position[0] if isinstance(position[0], int) else int(position[0] * screen_x),
        position[1] if isinstance(position[1], int) else int(position[1] * screen_y),
    )


def convert_size(position):
    """Convert a size in pixels of percentage to coordinates in inches"""
    if position is None:
        return None

    pos = convert_pos(position)

    px = 1 / plt.rcParams["figure.dpi"]

    return pos[0] * px, pos[1] * px


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
