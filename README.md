A simple GTK+ frontend for [LGOGDownloader](https://github.com/Sude-/lgogdownloader)
to enable support for the convenient `gogdownloader://` URIs GOG.com offers.

## Features

* Minimal but featureful GUI designed for comfort and convenience
* Anything not configurable via the GUI will obey lgogdownloader's
  `config.cfg`.

  ```rc
language = 1
limit-rate = 300
no-deb = false
no-language-packs = false
no-patches = false
no-subdirectories = false
no-targz = false
retries = 3
save-serials = true
  ```

* Support for selecting Linux downloads despite the site not offering
  `gogdownloader://` URIs for them

  ![linux selection screenshot](img/sshot_linux_select.png)

* Libnotify notification when all downloads are complete.

  ![notification screenshot](img/sshot_notification.png)

## Installation

```sh
# Get the dependencies
sudo apt-get install python-gtk2 python-dbus python-vte python-notify python-pip

# Unpack and install lgogd_uri
unzip lgogd_uri-master.zip
cd lgogd_uri-master
sudo pip install .    # Or `sudo ./setup.py install` if you don't need to uninstall

# Set it as your default handler for gogdownloader:// URIs
sudo update-desktop-database
xdg-mime default lgogd_uri.desktop x-scheme-handler/gogdownloader
```

This *should* make it work for both Firefox and Chrome, since both listen to
`xdg-mime default ...` but, depending on your version, you may need to restart
Firefox to get it to notice.

**Debugging:**

1. Run `xdg-open gogdownloader://ultima_4/installer_win_en` in a terminal.
   If that works, then your browser isn't obeying system defaults properly
   and your best bet is googling for questions about how to make BitTorrent
   magnet links work properly. (They use the same mechanism but are **much**
   more popular.)
2. Run `lgogd_uri gogdownloader://ultima_4/installer_win_en` in a terminal.
   If that works, but `xdg-open` doesn't, then it's installed but either the
   `lgogd_uri.desktop` file wasn't installed in the right place or the
   "Set it as your default handler" step failed.

Some of the things you can try are:

* Restarting your browser after it's all done

Depending on how your browser is
configured, you may need extra steps to make it


## Uninstallation

    sudo pip uninstall lgogd_uri

## Known Issues

* Multi-selection doesn't get along with GTKTreeView's built-in drag-and-drop
  reordering and context-menu support. (Use the Delete key for batch deletion)

## License

MIT except for three easy-to-replace platform logo icons copied from the
GOG.com site theme. (`windows.png`, `linux.png`, and `mac.png`)
