#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@todo:
 - Figure out how to properly handle install_requires for things which don't
   always install the requisite metadata for normal detection.
"""

__author__ = "Stephan Sokolow (deitarion/SSokolow)"
__license__ = "MIT"

import io, os, re

try:
    from setuptools import setup
except ImportError:
    # TODO: Verify that this branch actually works
    from distutils.core import setup

    from ez_setup import use_setuptools
    use_setuptools()

REQUIRES = []

# Detect PyGTK without requiring egg metadata
try:
    # pylint: disable=unused-import
    import gobject  # NOQA
except ImportError:
    REQUIRES.append('pygtk')

# Detect dbus-python without requiring egg metadata
try:
    # pylint: disable=unused-import
    import dbus  # NOQA
except ImportError:
    REQUIRES.append('dbus-python')

# Detect PyNotify without requiring egg metadata and support notify2 as well
try:
    # pylint: disable=unused-import
    import notify2  # NOQA
except ImportError:
    try:
        # pylint: disable=unused-import
        import pynotify  # NOQA
    except ImportError:
        REQUIRES.append('notify2')

# Detect VTE without requiring egg metadata
try:
    # pylint: disable=unused-import
    import vte  # NOQA
except ImportError:
    print("Your system lacks the Python bindings for libvte (python-vte) "
          "but they cannot be automatically installed by this script. "
          "Aborting.")
    import sys
    sys.exit(1)

# Get the version from the program rather than duplicating it here
# Source: https://packaging.python.org/en/latest/single_source_version.html
def read(*names, **kwargs):
    """Convenience wrapper for read()ing a file"""
    with io.open(os.path.join(os.path.dirname(__file__), *names),
              encoding=kwargs.get("encoding", "utf8")) as fobj:
        return fobj.read()

def find_version(*file_paths):
    """Extract the value of __version__ from the given file"""
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__\s*=\s*['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name="lgogd_uri",
    version=find_version("lgogd_uri", "main.py"),
    author="Stephan Sokolow (detarion/SSokolow)",
    author_email="http://www.ssokolow.com/ContactMe",
    description="Frontend to enable gogdownloader:// URLs in lgogdownloader",
    # TODO: long_description
    url="https://github.com/ssokolow/lgogd_uri",

    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: GTK",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet",
    ],
    install_requires=REQUIRES,
    keywords="gog lgogdownloader gui gtk downloadmanager download_manager",
    license="MIT",

    packages=['lgogd_uri'],
    package_data={'lgogd_uri': ['*.glade', '*.png']},
    data_files=[('share/applications', ['lgogd_uri.desktop'])],
    entry_points={'gui_scripts': ['lgogd_uri = lgogd_uri.main:main']}
)

# vim: set sw=4 sts=4 expandtab :
