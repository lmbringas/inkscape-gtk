import gi

gi.require_version("Gdk", "3.0")
gi.require_version('GooCanvas', '2.0')
from gi.repository import GooCanvas, Gdk

from .utils import to_rgba
from .marker import Marker, PointerMarker
from dataclasses import dataclass, field
from typing import List, Tuple


class Figure:
    ''''''
    def __init__(self, tbox):
        """Tarea comun: Buscar colores, y ancho del trazo actualmente
        seleccionados.
        """
        self.tbox = tbox

        self.stroke_color = to_rgba(self.tbox.stroke_colbtn.get_rgba())
        self.fill_color = to_rgba(self.tbox.fill_colbtn.get_rgba())
        self.line_width = self.tbox.spbtn.get_value()
        self.width = 0
        self.height = 0
        self.origin = None
        self.instance = None
        self.movement_marker = None
        self.scale_marker = None

    def remove(self):
        objects = [
            x
            for x in (self.movement_marker, self.scale_marker, self.instance)
            if x is not None
        ]
        for o in objects:
            o.remove()

    def set_w_h(self, w, h):
        self.width = w
        self.height = h
        x, y = self.origin[0], self.origin[1]

        if w < 0:
            x += w
            w = -w
        if h < 0:
            y += h
            h = -h

        self.set_x_y(x, y)
        self.instance.set_property('width', w)
        self.instance.set_property('height', h)

    def set_origin(self, x, y):
        self.origin = x, y

    def set_x_y(self, x, y):
        self.instance.set_property('x', x)
        self.instance.set_property('y', y)

    def move_to(self, x, y):
        new_x = x if self.width > 0 else x + self.width
        new_y = y if self.height > 0 else y + self.height
        self.set_x_y(new_x, new_y)
        self.set_origin(x, y)
        self.scale_marker.move_to(x + self.width, y + self.height)

    def resize(self, xnew, ynew):
        x, y = self.origin[0], self.origin[1]
        self.set_w_h(xnew - x, ynew - y)


class Rectangle(Figure):
    def __init__(self, tbox, x, y):
        super(Rectangle, self).__init__(tbox)
        self.set_origin(x, y)
        self.movement_marker = Marker(
            self.tbox.layer, x, y, color='Red', callback=self.move_to
        )

        self.instance = GooCanvas.CanvasRect(  # TODO
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
            'button-release-event', self.button_released
        )
        self.id_motion = tbox.layer.connect('motion-notify-event', self.button_moved)

    def button_released(self, src, tgt, event):
        w = event.x - self.origin[0]
        h = event.y - self.origin[1]
        self.set_w_h(w, h)

        self.tbox.layer.disconnect(self.id_release)
        self.tbox.layer.disconnect(self.id_motion)

        self.scale_marker = Marker(
            self.tbox.layer, event.x, event.y, color='Yellow', callback=self.resize
        )

    def button_moved(self, src, tgt, event):
        w = event.x - self.origin[0]
        h = event.y - self.origin[1]
        self.set_w_h(w, h)


class SimpleLine(Figure):
    def __init__(self, tbox, x, y):
        super(SimpleLine, self).__init__(tbox)
        self.tbox.layer.disconnect(self.tbox.layer_click_id)
        self.set_origin(x, y)
        self.closing_markers = [self.build_closing_marker(x, y)]
        self.connect_events()

        self.instance = GooCanvas.CanvasPolyline(
            parent=self.tbox.layer,
            fill_color_rgba=self.fill_color,
            stroke_color_rgba=self.stroke_color,
            line_width=self.line_width,
        )
        self.polyline_points = PolylinePoints(self.instance, x, y)

    def build_closing_marker(self, x, y):
        return PointerMarker(
            self.tbox.layer, x, y, color='grey', callback=self.close_polyline
        )

    def close_polyline(self, x, y):
        self.polyline_points.move_current(x, y)
        self.tbox.reconnect_layer_click()
        self.disconnect_events()
        self.remove_markers()
        self.create_scale_movement_markers()

    def create_scale_movement_markers(self):
        x = self.instance.get_property('x')
        y = self.instance.get_property('y')
        self.set_origin(x, y)
        self.movement_marker = Marker(
            self.tbox.layer, x, y, color='Red', callback=self.move_to
        )
        self.width = self.instance.get_property('width')
        self.height = self.instance.get_property('height')
        self.scale_marker = Marker(
            self.tbox.layer,
            x + self.width,
            y + self.height,
            color='Yellow',
            callback=self.resize,
        )

    def remove_markers(self):
        for marker in self.closing_markers:
            marker.remove()

    def connect_events(self):
        self.id_release = self.tbox.layer.connect(
            'button-press-event', self.canvas_clicked
        )
        self.id_motion = self.tbox.layer.connect(
            'motion-notify-event', self.pointer_moved
        )

    def disconnect_events(self):
        self.tbox.layer.disconnect(self.id_release)
        self.tbox.layer.disconnect(self.id_motion)

    def canvas_clicked(self, src, tgt, event):
        # if the event was triggred with a right-click
        if event.button == 3:
            self.close_polyline(event.x, event.y)
            self.polyline_points.remove_current()
            return

        self.polyline_points.move_current(event.x, event.y)
        self.polyline_points.add(event.x, event.y)
        self.closing_markers.append(self.build_closing_marker(event.x, event.y))

    def pointer_moved(self, src, tgt, event):
        self.polyline_points.move_current(event.x, event.y)

    def remove(self):
        super(SimpleLine, self).remove()
        self.remove_markers()


class PolylinePoints:
    def __init__(self, polyline, initial_x, initial_y):
        self.canvas_points = GooCanvas.CanvasPoints.new(0)
        self.polyline = polyline
        self.points = [(initial_x, initial_y)] * 2
        self.build_canvas_points()

    def build_canvas_points(self):
        self.canvas_points = GooCanvas.CanvasPoints.new(len(self.points))
        for i, point in enumerate(self.points):
            self.canvas_points.set_point(i, point[0], point[1])
        self.polyline.set_property('points', self.canvas_points)

    def add(self, x, y):
        self.points.append((x, y))
        self.build_canvas_points()

    def remove_current(self):
        self.points.pop()
        self.build_canvas_points()

    def move_current(self, x, y):
        self.points[-1] = (x, y)
        self.canvas_points.set_point(len(self.points) - 1, x, y)
        self.polyline.set_property('points', self.canvas_points)
