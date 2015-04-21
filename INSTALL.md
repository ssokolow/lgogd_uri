0. Make sure that Python 2.7, PyGTK, and dbus-python (`python-dbus` on
   Debian/Ubuntu/Mint) are installed.
1. Symlink `lgogd_uri.py` into your `$PATH`
2. Copy `lgogd_uri.desktop` into `/usr/share/applications/`
   or `~/.local/share/application/`
3. (optional) Add `x-scheme-handler/gogdownloader=lgogd_uri.desktop`
   to `~/.local/share/applications/mimeapps.list`
4. Run `sudo update-desktop-database`
5. (optional) Restart your browser
