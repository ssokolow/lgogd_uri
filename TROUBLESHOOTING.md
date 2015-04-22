# Troubleshooting

If your browser still doesn't want to handle `gogdownloader://` links after
running `install.sh`...

0. Try restarting your browser. It may only be checking your desktop
   configuration for changes on startup.

1. Run `xdg-open gogdownloader://ultima_4/installer_win_en` in a terminal.

   If that works, then lgogd_uri has been installed properly but your browser
   isn't obeying your desktop configuration.

   Your best bet for solving this is googling for questions about how to make
   BitTorrent `magnet:` links work properly. (They use the same mechanism but
   are **much** more popular.)

2. Run `lgogd_uri gogdownloader://ultima_4/installer_win_en` in a terminal.

   If that works, but `xdg-open` doesn't, then `lgogd_uri` was installed
   correctly but something about setting it as the default handler for
   `gogdownloader://` URIs failed.

   Verify that:

   * `lgogd_uri.desktop` was installed into `/usr/local/share/applications`
   * Your distro has left `/usr/local/share/applications` on the search path
     for `.desktop` files.
   * There is an `x-scheme-handler/gogdownloader=lgogd_uri.desktop` line in
     your `~/.local/share/applications/mimeapps.list`

   ...and then try rebooting in case some part of the mechanism for refreshing
   the desktop entry database without rebooting is broken on your system.

   If you receive an error other than "command not found", double-check that
   all required dependencies are installed, then file an
   [issue report](https://github.com/ssokolow/lgogd_uri/issues). Otherwise,
   continue troubleshooting.

3. Run `python -m lgogd_uri gogdownloader://ultima_4/installer_win_en` in a terminal.

   If this works but the previous step didn't, then lgogd_uri was properly
   installed in your `$PYTHONPATH` but outside your `$PATH`.

   If you don't want to continue troubleshooting:

   1. Run `sudo pip uninstall lgogd_uri` and then say `n` (no) when prompted to
      figure out where `lgogd_uri.desktop` was installed.
   2. Edit `lgogd_uri.desktop`, delete the `TryExec` line, and replace
      `Exec=lgogd_uri %U` with `Exec=python -m lgogd_uri %U`

   If you receive an error other than "No module named lgogd_uri", double-check
   that all required dependencies are installed, then file an
   [issue report](https://github.com/ssokolow/lgogd_uri/issues). Otherwise,
   continue troubleshooting.

4. Run `sudo pip uninstall lgogd_uri` and then say `n` (no) when prompted.

   If it says "Cannot uninstall requirement lgogd_uri, not installed", then
   the installation process failed and you should re-examine what `install.sh`
   was telling you in more detail.

   Otherwise, it will tell you where outside your `$PYTHONPATH` lgogd_uri was
   installed. If you don't want to troubleshoot that, copy `bin/lgogd_uri` file
   into your `$PATH` and return to the beginning of this guide.

