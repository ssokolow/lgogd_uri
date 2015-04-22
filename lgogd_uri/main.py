#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Wrapper for lgogdownloader to support queueing up gogdownloader:// URIs
Copyright (C) 2015 Stephan Sokolow

--snip--

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
__version__ = "0.1rc3"
__license__ = "MIT"

SVC_NAME = "com.ssokolow.lgogd_uri"
LGOGD_CFG_PATH = "~/.config/lgogdownloader/config.cfg"
GOGD_URI_CFG_PATH = "~/.config/lgogd_uri"
PLAT_WIN = 1
PLAT_MAC = 2
PLAT_LIN = 4
PLAT_DEF = 5  # Default
PLAT_ALL = 7
SUBDIR_GAME = '%gamename%'
SUBDIR_EXTRAS = 'extras'

import logging, os, subprocess, sys, time
from xml.etree import cElementTree as ET  # NOQA
log = logging.getLogger(__name__)

# Resolve the path to bundled icons only once
RES_DIR = os.path.dirname(os.path.realpath(__file__))

# ---=== Begin Imports ===---

try:
    import pygtk
    pygtk.require("2.0")
except ImportError:
    pass  # Apparently some PyGTK installs are missing this but still work

try:
    import gtk, gtk.gdk  # pylint: disable=import-error
except ImportError:
    sys.stderr.write("Missing PyGTK! Exiting.\n")
    sys.exit(1)

# Present tracebacks as non-fatal errors in the GUI for more user-friendliness
# TODO: In concert with this, I'll probably want some kind of failsafe
#       for re-enabling the Save button if necessary.
from lgogd_uri import gtkexcepthook
gtkexcepthook.enable()

try:
    import dbus, dbus.bus, dbus.service, dbus.mainloop.glib
except ImportError:
    sys.stderr.write("Missing dbus-python! Exiting.\n")
    sys.exit(1)

try:
    import notify2 as notify
except ImportError:
    try:
        import pynotify as notify
    except ImportError:
        log.warning("Missing libnotify bindings! Notifications will not show.")
        notify = None

try:
    import vte
except ImportError:
    vte = None

# ---=== Begin Functions ===---

def get_lgogd_conf():
    """Read and parse lgogdownloader's config file."""
    results = {}
    path = os.path.expanduser(LGOGD_CFG_PATH)
    if not os.path.exists(path):
        log.error("Cannot find LGOGDownloader config file at %s. "
                  "Falling back to internal defaults.", path)
        return results

    with open(os.path.expanduser(LGOGD_CFG_PATH)) as fobj:
        for line in fobj:
            try:
                key, val = [i.strip() for i in line.strip().split('=', 1)]
            except ValueError:
                continue  # Fail safely if a line doesn't contain =

            if val.lower() == 'true':
                val = True
            elif val.lower() == 'false':
                key = False
            else:
                try:
                    val = int(val)
                except ValueError:
                    pass

            results[key] = val
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

def which(execname, execpath=None):
    """Like the UNIX which command, this function attempts to find the given
    executable in the system's search path. Returns C{None} if it cannot find
    anything.
    """

    if isinstance(execpath, basestring):
        execpath = execpath.split(os.pathsep)
    elif not execpath:
        execpath = os.environ.get('PATH', os.defpath).split(os.pathsep)

    for path in execpath:
        fullpath = os.path.join(os.path.expanduser(path), execname)
        if os.path.exists(fullpath):
            return fullpath
    return None  # Couldn't find anything.

# ---=== Begin Application Class ===---

class Application(dbus.service.Object):  # pylint: disable=C0111,R0902
    def __init__(self, bus, path, name):
        dbus.service.Object.__init__(self, bus, path, name)
        self.running = False

        # Shut up PyLint about defining members in _init_gui
        self.builder = gtk.Builder()
        self.data = None
        self.toggle_map = {}
        self.lgd_conf = None
        self.notification = None
        self.term = None
        self.save_dir_store = os.path.expanduser(
            os.path.join(GOGD_URI_CFG_PATH, 'save_dir'))

    def _check_deps(self):
        """Return a message describing missing dependencies or C{None}."""
        if not vte:
            return "Missing python-vte! Exiting."
        if not which("lgogdownloader"):
            return "Cannot find lgogdownloader in $PATH! Exiting."

    def _init_gui(self):
        """Parts of __init__ that should only run in the single instance."""
        # Check for some deps late enough to display a GUI error message
        dep_err = self._check_deps()
        if dep_err:
            dlg = gtk.MessageDialog(None, gtk.DIALOG_MODAL,
                                    gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, dep_err)
            dlg.set_title("GOG Downloader")
            dlg.run()
            sys.exit(1)

        self.gtkbuilder_load('lgogd_uri.glade')
        self.data = self.builder.get_object('store_dlqueue')

        # Load the lgogdownloader settings
        self.lgd_conf = get_lgogd_conf()

        # Prepare a libnotify notification we can reuse
        if notify and notify.init("lgogd_uri"):
            self.notification = notify.Notification("GOG Downloads Complete",
                                                    icon='document-save')

        try:
            parent = os.path.dirname(self.save_dir_store)
            if not os.path.exists(parent):
                os.makedirs(parent)
        except OSError, err:
            log.error("Cannot prepare to remember target directory: %s", err)

        # Set the default target directory to the user's Downloads folder
        try:
            tgt_path = subprocess.check_output(
                ["xdg-user-dir", "DOWNLOAD"]).strip()
        except (OSError, subprocess.CalledProcessError):
            tgt_path = os.path.expanduser("~")
        # Remember the user's customized choice
        if os.path.exists(self.save_dir_store):
            with open(self.save_dir_store, 'r') as fobj:
                tgt_path = fobj.read().strip()
        self.builder.get_object('btn_target').set_filename(tgt_path)

        # FIXME: Figure out how to preserve multi-select during drag-start
        tview = self.builder.get_object("view_dlqueue")
        tview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)

        # VTE widgets aren't offered by Glade. Add and config at runtime.
        self.term = vte.Terminal()
        self.term.connect("child-exited", self.on_child_exited)
        self.builder.get_object("vbox_term").add(self.term)

        mainwin = self.builder.get_object('mainwin')
        mainwin.set_title('%s %s' % (mainwin.get_title(), __version__))
        mainwin.show_all()

    def gtkbuilder_load(self, path):
        """Wrapper to work around the brokenness of
        GtkCellRendererToggle.set_active() and the inability to retrieve
        attributes from columns once set.
        """
        path = os.path.join(RES_DIR, path)
        self.builder.add_from_file(os.path.join(RES_DIR, path))
        self.builder.connect_signals(self)

        # Retrieve the view-store mappings from the raw GTK Builder XML
        # because PyGTK lacks an API for retrieving them from the widgets.
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

    @dbus.service.method(SVC_NAME, in_signature='', out_signature='b')
    def is_running(self):
        """D-Bus method required to implement startup notification."""
        return self.running

    def enqueue_uris(self, arguments):
        """Code common to launch and raise sides of single instancing."""
        platforms = self.lgd_conf.get('platform', PLAT_DEF)

        iter_last = None
        for arg in arguments:
            for game_id, file_id in parse_uri(arg):
                is_patch = 'patch' in file_id

                # is_installer triggers the UI and code for allowing Win/Mac
                # links to result in Linux downloads, so patches are also
                # installers for our purposes.
                is_installer = ('installer' in file_id) or is_patch

                # Used by cell visibility binding
                not_installer = is_patch or (not is_installer)

                iter_last = self.data.append((
                    game_id,
                    file_id,
                    is_installer,
                    platforms & PLAT_WIN,
                    platforms & PLAT_LIN,
                    platforms & PLAT_MAC,
                    not_installer,
                    is_patch))

        # Ensure that all added entries are made visible unless the window
        # isn't tall enough.
        if iter_last:
            path_last = self.data.get_path(iter_last)
            self.builder.get_object('view_dlqueue').scroll_to_cell(path_last)

    def gtk_main_quit(self, widget, event):  # pylint: disable=R0201,W0613
        """Helper for Builder.connect_signals"""
        gtk.main_quit()

    def next_download(self):
        """Common code for the Save button and lgogdownloader exit handler"""
        queue_iter = self.data.get_iter_first()
        if not queue_iter:
            # Do this as early as possible to minimize the chance that
            # an exception caught by gtkexcepthook.py will leave btn_go grayed
            self.builder.get_object('btn_go').set_sensitive(True)
            self.term.feed("\r\n** Done. (Queue emptied) **\r\n")
            try:
                self.notification.show()
            except dbus.DBusException, err:
                log.error("Could not show notification: %s", err)
            return

        no_subdirs = self.lgd_conf.get('no-subdirectories', False)

        # TODO: Rather than popping it off the store, use a status column
        #       so that users can easily see and retry failed downloads.
        (game_id, file_id, is_inst, win, lin, mac, is_patch
         ) = self.data.get(queue_iter, 0, 1, 2, 3, 4, 5, 7)
        self.data.remove(queue_iter)

        subdirs = {}
        for key, default in (
                ('subdir-game', SUBDIR_GAME),
                ('subdir-extras', SUBDIR_EXTRAS)):
            subdirs[key] = self.lgd_conf.get(key, default)

            # Limited support for --subdir-game and --subdir-extras
            subdirs[key] = subdirs[key].replace('%gamename%', game_id)

        tgt = self.builder.get_object('btn_target').get_filename()
        cmd = ['lgogdownloader']
        if is_inst:
            self.term.feed("\rRetrieving your shelf. This may take time.\r\n")
            if is_patch:
                cmd.extend(['--platform',
                            str((win * PLAT_WIN) +
                               (lin * PLAT_LIN) +
                               (mac * PLAT_MAC)),
                            '--download', '--no-extras', '--no-installers',
                            '--game', '^%s$' % game_id])
            else:
                cmd.extend(['--platform',
                            str((win * PLAT_WIN) +
                               (lin * PLAT_LIN) +
                               (mac * PLAT_MAC)),
                            '--download', '--no-extras',
                            '--game', '^%s$' % game_id])
        else:
            do_fix = self.builder.get_object("chk_path_fixup").get_active()
            if do_fix and not no_subdirs:
                tgt = os.path.join(tgt,
                                   subdirs['subdir-game'],
                                   subdirs['subdir-extras'])
                if not os.path.exists(tgt):
                    # TODO: Decide how to handle failure here gracefully
                    os.makedirs(tgt)

            path = "%s/%s" % (game_id, file_id)
            cmd.extend(['--download-file', path])

        self.term.fork_command(cmd[0], cmd, None, tgt)

    def on_btn_go_clicked(self, widget, event=None):  # pylint: disable=W0613
        """Callback for the 'Save' button"""
        nbook = self.builder.get_object('nbook_main')
        nbook.set_show_tabs(True)
        nbook.set_current_page(nbook.page_num(
            self.builder.get_object("vbox_term")))
        self.next_download()

        # Do this as late as possible to minimize the chance that an exception
        # could leave it un-sensitive
        widget.set_sensitive(False)

    def on_btn_target_file_set(self, widget):
        """Handler to persist changes to the target directory"""
        try:
            with open(self.save_dir_store, 'w') as fobj:
                fobj.write(widget.get_filename())
        except IOError, err:
            log.error("Cannot save target directory: %s", err)

    def on_cell_toggled(self, cellrenderer, path):
        """Handler for enabling clicks on checkbox cells."""
        idx = self.toggle_map[cellrenderer]
        self.data[path][idx] = not self.data[path][idx]

    def on_child_exited(self, widget):
        """Handler to start next download when lgogdownloader exits."""
        if widget.get_child_exit_status() != 0:
            # TODO: Redesign the queue so this can be indicated by icons
            widget.feed("\r\n-- DOWNLOAD FAILED --")
        self.next_download()

    # pylint: disable=no-self-use
    def on_view_dlqueue_key_press_event(self, widget, event):
        """Handler for enabling the Delete key"""
        if (event.type == gtk.gdk.KEY_PRESS and
                event.keyval == gtk.keysyms.Delete):
            model, rows = widget.get_selection().get_selected_rows()
            rows = [gtk.TreeRowReference(model, x) for x in rows]
            for ref in rows:
                model.remove(model.get_iter(ref.get_path()))

    # pylint: disable=unused-argument,invalid-name
    def on_view_dlqueue_button_press_event(self, widget, event=None):
        """Right-click and Menu button handler for the TreeView.

        Source: http://faq.pygtk.org/index.py?req=show&file=faq13.017.htp
        """
        treeview = self.builder.get_object('view_dlqueue')
        if event and event.button == 3:  # Right Click
            btn = event.button
            x, y, time = int(event.x), int(event.y), event.time
        elif event:                      # Non-right Click
            return None
        elif not event:                  # Menu key on the keyboard
            cursor = treeview.get_cursor()
            if cursor[0] is None:
                return None

            x, y, _, _ = treeview.get_cell_area(*cursor)
            btn, time = 3, 0

        pthinfo = treeview.get_path_at_pos(x, y)
        if pthinfo is not None:
            path, col, _, _ = pthinfo
            treeview.grab_focus()
            treeview.set_cursor(path, col, 0)
        self.builder.get_object("popup_dlqueue").popup(
            None, None, None, btn, time)
        return True

    # pylint: disable=no-self-use
    def on_view_dlqueue_scroll_event(self, widget, event):
        """Generic handler to enable the scroll-wheel in a TreeView"""
        adj = widget.get_vadjustment()
        cur, incr = adj.get_value(), adj.get_page_increment() / 2.0
        if event.direction == gtk.gdk.SCROLL_UP:
            adj.set_value(cur - incr)
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            adj.set_value(min(
                cur + incr, adj.get_upper() - adj.get_page_increment()))

    def on_dlqueue_delete_activate(self, widget):
        """Handler to allow TreeView entry deletion"""
        path = self.builder.get_object('view_dlqueue').get_cursor()[0]
        if path:
            self.data.remove(self.data.get_iter(path))

    @dbus.service.method(SVC_NAME, in_signature='a{sv}asi', out_signature='')
    def start(self, options, arguments, timestamp):
        """The part of main() which should run in the single instance"""
        if self.is_running():
            self.enqueue_uris(arguments)
            nbook = self.builder.get_object('nbook_main')
            nbook.set_current_page(nbook.page_num(
                self.builder.get_object("vbox_queue")))
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
            usage="%prog [options] <gogdownloader URI> ...",
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
    request = bus.request_name(SVC_NAME, dbus.bus.NAME_FLAG_DO_NOT_QUEUE)
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
