A simple GTK+ frontend for [LGOGDownloader](https://github.com/Sude-/lgogdownloader)
to enable support for the convenient `gogdownloader://` URIs that
[GOG.com](http://www.gog.com/) offers.

## Features

* Minimal but featureful queueing GUI designed for comfort and convenience

  ![main window screenshot](img/sshot_mainwin.png)

* Built-in terminal for lgogdownloader status without making your window
  manager sweat.

  ![terminal tab screenshot](img/sshot_term.png)

* Anything not configurable via the GUI will obey lgogdownloader's
  `config.cfg`.

  ```ini
language = 1
limit-rate = 300
no-targz = true
retries = 3
save-serials = true
  ```

* Remembers your preferred destination directory

  !["Save Into" screenshot](img/sshot_save_into.png)

* Support for selecting Linux downloads despite the site not offering
  `gogdownloader://` URIs for them

  ![linux selection screenshot](img/sshot_linux_select.png)

* Libnotify notification when all downloads are complete.

  ![notification screenshot](img/sshot_notification.png)

* Add, reorder, and delete remaining queue entries while a download is in
  progress. (Including changing the target directory for future downloads)

  ![tabs screenshot](img/sshot_tabs.png)

## Installation

Just run `sh install.sh` and follow the instructions.

(Running `setup.py` directly cannot install non-PyPI dependencies like PyGTK
 and also will not register the application as your default handler for
 `gogdownloader://` URIs.)

The installation process has been fully automated for users on Debian-based
distros (eg. Ubuntu, Mint) while users on other distros will be asked to
manually install a list of dependencies.

At present, only system-wide installation is supported but feel free to
examine what the script is doing before you run it.

### Troubleshooting:

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## Uninstallation

    sudo pip uninstall lgogd_uri

## Known Shortcomings

* Providing the option to download Linux versions via the Windows or MacOS
  `gogdownloader://` URLs has resulted in the language-selection drop-down
  being ignored in favour of the `language` option in lgogdownloader's
  `config.cfg`
* Multi-selection doesn't get along with GTKTreeView's built-in drag-and-drop
  reordering and context-menu support. (Use the Delete key for batch deletion)
* Remembering un-finished downloads across a restart is still on the TODO list.
* Currently, no attempt is made to retrieve game metadata, so the "Game" and
  "File ID" columns don't give the nice, pretty output the official GOG
  downloader offers and the platform checkboxes will always start out set
  to the value of `platform` in your `config.cfg`.
* No attempt is currently made to deduplicate the queue, relying instead on
  LGOGDownloader to not redownload files which already exist.
* Fixup support for `--download-file` currently only resolves `%gamename%`

## License

[MIT](http://opensource.org/licenses/MIT) except for three easy-to-replace
platform logo icons copied from the GOG.com site theme.

* `windows.png`
* `linux.png`
* `mac.png`
