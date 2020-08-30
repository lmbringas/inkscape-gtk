import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GdkPixbuf
from figures import Rectangle, SimpleLine
from figures.utils import make_rgba


DEFAULT_STROKE_COLOR = make_rgba("cyan")
DEFAULT_FILL_COLOR = make_rgba("khaki", 0.5)


class Toolbox(Gtk.Frame):
    def __init__(self, layer):
        super(Toolbox, self).__init__(label="Herramientas", margin=6)
        self.layer = layer
        self.layer_click_id = self.layer.connect("button-press-event", self.layer_click)
        self.figure = None
        self.figures = []

        vbox = Gtk.VBox(margin=6)
        self.add(vbox)

        lbl = Gtk.Label(label="Ancho trazo:", xalign=0)
        vbox.pack_start(lbl, False, False, 0)
        self.spbtn = Gtk.SpinButton.new_with_range(0, 20, 0.1)
        self.spbtn.set_value(1.0)
        vbox.pack_start(self.spbtn, False, False, 0)

        lbl = Gtk.Label(label="Color trazo:", xalign=0)
        vbox.pack_start(lbl, False, False, 0)
        self.stroke_colbtn = Gtk.ColorButton(use_alpha=True, rgba=DEFAULT_STROKE_COLOR)
        vbox.pack_start(self.stroke_colbtn, False, False, 0)

        lbl = Gtk.Label(label="Color relleno:", xalign=0)
        vbox.pack_start(lbl, False, False, 0)
        self.fill_colbtn = Gtk.ColorButton(use_alpha=True, rgba=DEFAULT_FILL_COLOR)
        vbox.pack_start(self.fill_colbtn, False, False, 0)

        lbl = Gtk.Label(label="Figuras:", xalign=0)
        vbox.pack_start(lbl, False, False, 0)

        for file, tooltip, figure in (
            ("assets/rectangle.svg", "Rectángulo", Rectangle),
            ("assets/ellipse.svg", "Ellipse", None),
            ("assets/line.svg", "Líneas", SimpleLine),
            ("assets/qbezier.svg", "Bézier Cuadratico", None),
            ("assets/cbezier.svg", "Bézier Cúbico", None),
        ):
            try:
                pxb = GdkPixbuf.Pixbuf.new_from_file_at_scale(file, -1, 32, True)
                img = Gtk.Image.new_from_pixbuf(pxb)
            except:
                img = Gtk.Image.new_from_file("invalid")
            btn = Gtk.Button(
                image=img, tooltip_text=tooltip, relief=Gtk.ReliefStyle.NONE
            )
            btn.connect("clicked", self.figure_selected, figure)
            vbox.pack_start(btn, False, False, 0)

        clear_button = Gtk.Button.new_with_label("Limpiar")
        clear_button.connect("clicked", self.clear)
        vbox.pack_end(clear_button, False, False, 0)

    def reconnect_layer_click(self):
        self.layer_click_id = self.layer.connect('button-press-event', self.layer_click)

    def figure_selected(self, btn, which):
        self.figure = which

    def layer_click(self, src, tgt, event):
        if self.figure is not None:
            # self.figure contiene al objeto a instanciar - lo hacemos aqui.
            self.figures.append(self.figure(self, event.x, event.y))

    def clear(self, btn):
        if self.figures:
            for figure in self.figures:
                figure.remove()
            self.figures.clear()
