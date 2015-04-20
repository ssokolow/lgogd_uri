#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Wrapper for lgogdownloader to support queueing up gogdownloader:// URIs
Copyright (C) 2015 Stephan Sokolow

Thanks to Luca "Lethalman" Bruno for the code to implement a single-instance
application via D-Bus.
http://lethalman.blogspot.ca/2008/11/single-app-instances-python-and-dbus.html

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

from __future__ import (absolute_import, division, print_function,
                        with_statement, unicode_literals)

__author__ = "Stephan Sokolow (deitarion/SSokolow)"
__appname__ = "URI handler for lgogdownloader"
__version__ = "0.0pre0"
__license__ = "MIT"

SVC_NAME = "com.ssokolow.lgogd_uri"
PLAT_WIN = 1
PLAT_MAC = 2
PLAT_LIN = 4
PLAT_DEF = 5  # Default
PLAT_ALL = 7

import logging, os, subprocess, time
from xml.etree import cElementTree as ET
log = logging.getLogger(__name__)

RES_DIR = os.path.dirname(os.path.realpath(__file__))

try:
    import pygtk
    pygtk.require("2.0")
except ImportError:
    pass

import dbus, dbus.bus, dbus.service, dbus.mainloop.glib
import gobject, gtk, gtk.gdk

def get_lgogd_conf():
    """Read and parse lgogdownloader's config file."""
    results = {}
    with open(os.path.expanduser("~/.config/lgogdownloader/config.cfg")) as fh:
        for line in fh:
            x, y = [i.strip() for i in line.strip().split('=',1)]
            if y.lower() == 'true':
                y = True
            elif y.lower() == 'false':
                y = False
            else:
                try:
                    y = int(y)
                except ValueError:
                    pass

            results[x] = y
    return results

def parse_uri(uri):
    """Parse a gogdownloader:// URI into a list of (game,file_id) tuples"""
    scheme_prefix = 'gogdownloader://'

    if not uri.lower().startswith(scheme_prefix):
        raise ValueError("Not a valid GOGDownloader URI: %s" % uri)

    results = []
    for filepath in uri[len(scheme_prefix):].strip().split(','):
        filepath = filepath.strip()
        if '/' not in filepath:
            filepath += '/'
        results.append(tuple(filepath.split('/', 1)))
    return results

class Application(dbus.service.Object):
    def __init__(self, bus, path, name):
        dbus.service.Object.__init__(self, bus, path, name)
        self.running = False

        # Shut up PyLint
        self.builder = gtk.Builder()
        self.toggle_map = {}
        self.conf = None
        self.data = None

    def _init_gui(self):
        """Parts of __init__ that should only run in the single instance."""
        self.gtkbuilder_load('lgogd_uri.glade')

        # Load the lgogdownloader settings
        self.conf = get_lgogd_conf()

        # TODO: Save customized values
        tgt_path = subprocess.check_output(
            ["xdg-user-dir", "DOWNLOAD"]).strip()
        self.builder.get_object('btn_target').set_filename(tgt_path)

        self.data = self.builder.get_object('store_dlqueue')
        self.builder.get_object('mainwin').show_all()

    def gtkbuilder_load(self, path):
        """Wrapper to work around the brokenness of
        GtkCellRendererToggle.set_active() and the inability to retrieve
        attributes from columns once set.
        """
        path = os.path.join(RES_DIR, path)
        self.builder.add_from_file(os.path.join(RES_DIR, path))

        columns = ET.parse(path).findall(".//*[@class='GtkTreeViewColumn']")
        for column in columns:
            renderer = column.find(".//*[@class='GtkCellRendererToggle']")
            # ElementTree doesn't implement parent traversal or we could find
            # this and then walk up
            if renderer:
                obj = self.builder.get_object(renderer.get('id'))
                idx = column.find(".//attributes/attribute[@name='active']")
                if idx is not None:
                    self.toggle_map[obj] = int(idx.text)

        self.builder.connect_signals(self)

    @dbus.service.method(SVC_NAME, in_signature='', out_signature='b')
    def is_running(self):
        return self.running

    def enqueue_uris(self, arguments):
        platforms = self.conf.get('platform', PLAT_DEF)

        rows = []
        for arg in arguments:
            for entry in parse_uri(arg):
                self.data.append(entry + (
                    platforms & PLAT_WIN,
                    platforms & PLAT_LIN,
                    platforms & PLAT_MAC))
        return rows

    def gtk_main_quit(self, widget, event):
        """Helper for Builder.connect_signals"""
        gtk.main_quit()

    def on_cell_toggled(self, cellrenderer, path):
        """Handler for enabling clicks on checkbox cells."""
        idx = self.toggle_map[cellrenderer]
        self.data[path][idx] = not self.data[path][idx]

    def on_view_dlqueue_key_press_event(self, widget, event):
        """Handler for enabling the Delete key"""
        if (event.type == gtk.gdk.KEY_PRESS and
                event.keyval == gtk.keysyms.Delete):
            path = widget.get_cursor()[0]
            if path:
                self.data.remove(self.data.get_iter(path))

    def on_view_dlqueue_button_press_event(self, widget, event=None):
        treeview = self.builder.get_object('view_dlqueue')
        if event and event.button == 3:
                btn = event.button
                x, y, time = int(event.x), int(event.y), event.time
        elif event:
            return None
        elif not event:  # Menu key on the keyboard
                cursor = treeview.get_cursor()
                if not cursor[0]:
                    return None

                x, y, _, _ = treeview.get_cell_area(*cursor)
                btn, time = 3, 0

        pthinfo = treeview.get_path_at_pos(x, y)
        if pthinfo is not None:
            path, col, cellx, celly = pthinfo
            treeview.grab_focus()
            treeview.set_cursor( path, col, 0)
        self.builder.get_object("popup_dlqueue").popup(
            None, None, None, btn, time)
        return True

    def on_dlqueue_delete_activate(self, widget):
        path = self.builder.get_object('view_dlqueue').get_cursor()[0]
        if path:
            self.data.remove(self.data.get_iter(path))

    @dbus.service.method(SVC_NAME, in_signature='a{sv}asi', out_signature='')
    def start(self, options, arguments, timestamp):
        import os

        if self.is_running():
            self.enqueue_uris(arguments)
            self.builder.get_object('mainwin').present_with_time(timestamp)
        else:
            self.running = True
            self._init_gui()
            self.enqueue_uris(arguments)
            gtk.main()
            self.running = False

def main():
    """The main entry point, compatible with setuptools entry points."""
    from optparse import OptionParser
    parser = OptionParser(version="%%prog v%s" % __version__,
            usage="%prog [options] <argument> ...",
            description=__doc__.replace('\r\n', '\n').split('\n--snip--\n')[0])
    parser.add_option('-v', '--verbose', action="count", dest="verbose",
        default=2, help="Increase the verbosity. Use twice for extra effect")
    parser.add_option('-q', '--quiet', action="count", dest="quiet",
        default=0, help="Decrease the verbosity. Use twice for extra effect")
    # Reminder: %default can be used in help strings.

    # Allow pre-formatted descriptions
    parser.formatter.format_description = lambda description: description

    opts, args = parser.parse_args()

    # Set up clean logging to stderr
    log_levels = [logging.CRITICAL, logging.ERROR, logging.WARNING,
                  logging.INFO, logging.DEBUG]
    opts.verbose = min(opts.verbose - opts.quiet, len(log_levels) - 1)
    opts.verbose = max(opts.verbose, 0)
    logging.basicConfig(level=log_levels[opts.verbose],
                        format='%(levelname)s: %(message)s')

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SessionBus()
    request = bus.request_name("com.ssokolow.lgogd_uri",
                               dbus.bus.NAME_FLAG_DO_NOT_QUEUE)
    if request != dbus.bus.REQUEST_NAME_REPLY_EXISTS:
        app = Application(bus, '/', SVC_NAME)
    else:
        obj = bus.get_object(SVC_NAME, "/")
        app = dbus.Interface(obj, SVC_NAME)

    app.start(vars(opts), args, int(time.time()))
    if app.is_running():
        gtk.gdk.notify_startup_complete()

if __name__ == '__main__':
    main()

# vim: set sw=4 sts=4 expandtab :
