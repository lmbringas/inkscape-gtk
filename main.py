#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  demo_window.py
#
#  Copyright 2020 John Coppens <john@jcoppens.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#


import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GooCanvas", "2.0")
from gi.repository import Gtk, GooCanvas
from toolbox import Toolbox


class MainWindow(Gtk.Window):
    def __init__(self):
        super(MainWindow, self).__init__(title="inkscape 2 ")
        self.connect("destroy", self.quit)
        self.set_default_size(600, 600)

        canvas = GooCanvas.Canvas(
            hexpand=True,
            vexpand=True,
        )
        cvroot = canvas.get_root_item()

        scroller = Gtk.ScrolledWindow()
        scroller.add(canvas)

        toolbox = Toolbox(cvroot)

        grid = Gtk.Grid()
        grid.attach(scroller, 0, 0, 1, 1)
        grid.attach(toolbox, 1, 0, 1, 1)

        self.add(grid)

        self.show_all()

    def quit(self, event):
        Gtk.main_quit()

    def run(self):
        Gtk.main()


def main(args):
    mainwdw = MainWindow()
    mainwdw.run()

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main(sys.argv))
