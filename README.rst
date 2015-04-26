.. image:: https://landscape.io/github/ssokolow/lgogd_uri/master/landscape.svg?style=flat
   :target: https://landscape.io/github/ssokolow/lgogd_uri/master
   :alt: Code Health
.. image:: https://codeclimate.com/github/ssokolow/lgogd_uri/badges/gpa.svg
   :target: https://codeclimate.com/github/ssokolow/lgogd_uri
   :alt: Code Climate
.. image:: https://scrutinizer-ci.com/g/ssokolow/lgogd_uri/badges/quality-score.png?b=master
   :target: https://scrutinizer-ci.com/g/ssokolow/lgogd_uri/?branch=master
   :alt: Scrutinizer Code Quality
.. image:: https://www.codacy.com/project/badge/09670e4eac6c4ad1852d0fe5a4f8884e
   :target: https://www.codacy.com/app/from_github/lgogd_uri
   :alt: Codacy Badge

A simple GTK+ frontend for `LGOGDownloader`_
to enable support for the convenient ``gogdownloader://`` URIs that
`GOG.com`_ offers.

--------
Features
--------

* Minimal but featureful queueing GUI designed for comfort and convenience

  .. image:: img/sshot_mainwin.png
     :alt: main window screenshot

* Built-in terminal for lgogdownloader status without making your window
  manager sweat.

  .. image:: img/sshot_term.png
     :alt: terminal tab screenshot

* Anything not configurable via the GUI will obey lgogdownloader's
  ``config.cfg``.

  .. code-block:: ini

     language = 1
     limit-rate = 300
     no-targz = true
     retries = 3
     save-serials = true

* Remembers your preferred destination directory

  .. image:: img/sshot_save_into.png
     :alt: "Save Into" screenshot

* Support for selecting Linux downloads despite the site not offering
  ``gogdownloader://`` URIs for them

  .. image:: img/sshot_linux_select.png
     :alt: linux selection screenshot

* Libnotify notification when all downloads are complete.

  .. image:: img/sshot_notification.png
     :alt: [notification screenshot

* Add, reorder, and delete remaining queue entries while a download is in
  progress. (Including changing the target directory for future downloads)

  .. image:: img/sshot_tabs.png
     :alt: tabs screenshot

------------
Installation
------------

Just run ``sh install.sh`` and follow the instructions. (Depending on your
desktop environment, you may also be able to just double-click ``install.sh``)

(Running ``setup.py`` directly cannot install non-PyPI dependencies like PyGTK
and also will not register the application as your default handler for
``gogdownloader://`` URIs.)

The installation process has been fully automated for users on Debian-based
distros (eg. Ubuntu, Mint) while users on other distros will be asked to
manually install a list of dependencies.

At present, only system-wide installation is supported but feel free to
examine what the script is doing before you run it.

Troubleshooting:
----------------

See `TROUBLESHOOTING.rst`_

--------------
Uninstallation
--------------

    sudo pip uninstall lgogd_uri

------------------
Known Shortcomings
------------------

* Providing the option to download Linux versions via the Windows or MacOS
  ``gogdownloader://`` URLs has resulted in the language-selection drop-down
  being ignored in favour of the ``language`` option in lgogdownloader's
  ``config.cfg``
* Multi-selection doesn't get along with ``GtkTreeView``'s built-in
  drag-and-drop reordering and context-menu support. (Use the Delete key for
  batch deletion)
* Remembering un-finished downloads across a restart is still on the TODO list.
* Currently, no attempt is made to retrieve game metadata, so the "Game" and
  "File ID" columns don't give the nice, pretty output the official GOG
  downloader offers and the platform checkboxes will always start out set
  to the value of ``platform`` in your ``config.cfg``.
* No attempt is currently made to deduplicate the queue, relying instead on
  LGOGDownloader to not redownload files which already exist.
* Fixup support for ``--download-file`` currently only resolves ``%gamename%``

-------
License
-------

MIT_ except for three easy-to-replace platform logo icons copied from the
GOG.com_ site theme.

* ``windows.png``
* ``linux.png``
* ``mac.png``



.. _GOG.com: http://www.gog.com/
.. _LGOGDownloader: https://github.com/Sude-/lgogdownloader
.. _MIT: http://opensource.org/licenses/MIT
.. _TROUBLESHOOTING.rst: TROUBLESHOOTING.rst
