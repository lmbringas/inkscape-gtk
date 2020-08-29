import gi

gi.require_version("Gdk", "3.0")
from gi.repository import Gdk


def make_rgba(color_string, alpha=1):
    c = Gdk.RGBA()
    c.parse(color_string)
    c.alpha = alpha
    return c


def to_rgba(color):
    """Conversion de formato Gdk.RGBA (r, g, b y a en valores de 0 a 1.0)
    resultado de get_rgba) a integer para GooCanvas.
    """
    return (
        (int(color.red * 255) << 24)
        + (int(color.green * 255) << 16)
        + (int(color.blue * 255) << 8)
        + int(color.alpha * 255)
    )
