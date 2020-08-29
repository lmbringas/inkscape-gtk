import gi

gi.require_version("GooCanvas", "2.0")
from gi.repository import GooCanvas


from .utils import to_rgba
from .marker import Marker


class Figure:
    """"""

    def __init__(self, tbox):
        """Tarea comun: Buscar colores, y ancho del trazo actualmente
        seleccionados.
        """
        self.tbox = tbox

        self.stroke_color = to_rgba(self.tbox.stroke_colbtn.get_rgba())
        self.fill_color = to_rgba(self.tbox.fill_colbtn.get_rgba())
        self.line_width = self.tbox.spbtn.get_value()


class Rectangle(Figure):
    def __init__(self, tbox, x, y):
        super(Rectangle, self).__init__(tbox)
        self.origin = x, y
        self.marker1 = Marker(self.tbox.layer, x, y, color="Red", callback=self.moveto)

        self.rect = GooCanvas.CanvasRect(  # TODO
            parent=tbox.layer,
            x=x,
            y=y,
            width=0,
            height=0,
            fill_color_rgba=self.fill_color,
            stroke_color_rgba=self.stroke_color,
            line_width=self.line_width,
        )

        self.id_release = tbox.layer.connect(
            "button-release-event", self.button_released
        )
        self.id_motion = tbox.layer.connect("motion-notify-event", self.button_moved)

    def set_x_y(self, x, y):
        self.rect.set_property("x", x)
        self.rect.set_property("y", y)

    def get_x_y(self):
        return (self.rect.get_property("x"), self.rect.get_property("y"))

    def set_w_h(self, w, h):
        x, y = self.get_x_y()

        if w < 0:
            x += w
            w = -w
        if h < 0:
            y += h
            h = -h

        self.set_x_y(x, y)
        self.rect.set_property("width", w)
        self.rect.set_property("height", h)

    def button_released(self, src, tgt, event):
        w = event.x - self.origin[0]
        h = event.y - self.origin[1]
        self.set_w_h(w, h)

        self.tbox.layer.disconnect(self.id_release)
        self.tbox.layer.disconnect(self.id_motion)

        self.marker2 = Marker(
            self.tbox.layer, event.x, event.y, color="Yellow", callback=self.resize
        )

    def moveto(self, x, y):
        self.set_x_y(x, y)
        w = self.rect.get_property("width")
        h = self.rect.get_property("height")
        self.marker2.moveto(x + w, y + h)

    def resize(self, xnew, ynew):
        x, y = self.get_x_y()
        self.set_w_h(xnew - x, ynew - y)

    def button_moved(self, src, tgt, event):
        w = event.x - self.origin[0]
        h = event.y - self.origin[1]
        self.set_w_h(w, h)


class SimpleLine(Figure):
    def __init__(self, tbox, x, y):
        super(SimpleLine, self).__init__(tbox)
        self.origin = x, y
        self.marker1 = Marker(self.tbox.layer, x, y, color="Red", callback=self.moveto)

        self.id_release = tbox.layer.connect(
            "button-release-event", self.button_released
        )

        self.id_motion = tbox.layer.connect("motion-notify-event", self.button_moved)

        self.points = GooCanvas.CanvasPoints.new(2)
        self.points.set_point(0, x, y)
        self.points.set_point(1, x, y)
        self.line = GooCanvas.CanvasPolyline(
            parent=self.tbox.layer,
            points=self.points,
            stroke_color="Orange",
            line_width=2,
        )

    def set_x_y(self, x, y):
        self.line.set_property("x", x)
        self.line.set_property("y", y)

    def moveto(self, x, y):
        self.set_x_y(x, y)
        w = self.line.get_property("width")
        h = self.line.get_property("height")
        self.marker2.moveto(x + w, y + h)

    def get_x_y(self):
        return (self.line.get_property("x"), self.line.get_property("y"))

    def resize(self, xnew, ynew):
        x, y = self.get_x_y()
        self.set_x_y(x, y)
        self.line.set_property("width", xnew - x)
        self.line.set_property("height", ynew - y)

    def button_released(self, src, tgt, event):
        self.tbox.layer.disconnect(self.id_release)
        self.tbox.layer.disconnect(self.id_motion)

        self.points.set_point(1, event.x, event.y)
        self.line.set_property("points", self.points)
        self.marker2 = Marker(
            self.tbox.layer, event.x, event.y, color="Yellow", callback=self.resize
        )

    def button_moved(self, src, tgt, event):
        self.points.set_point(1, event.x, event.y)
        self.line.set_property("points", self.points)
