#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Best attempt at a robust setup.py for a PyGTK app"""

__author__ = "Stephan Sokolow (deitarion/SSokolow)"
__license__ = "MIT"

import io, os, re, sys

try:
    from setuptools import setup
except ImportError:
    # TODO: Verify that this branch actually works
    from distutils.core import setup

    from ez_setup import use_setuptools
    use_setuptools()

# Requirements adapter for packages which may not be PyPI-installable
REQUIRES = []

def test_for_imports(choices, package_name, human_package_name):
    """Detect packages without requiring egg metadata

    Fallback to either adding an install_requires entry or exiting with
    an error message.
    """
    if os.environ.get("IS_BUILDING_PACKAGE", None):
        return  # Allow packaging without runtime-only deps installed

    if isinstance(choices, basestring):
        choices = [choices]

    while choices:
        # Detect PyGTK without requiring egg metadata
        try:
            current = choices.pop(0)
            __import__(current)
        except ImportError:
            if choices:  # Allow a fallback chain
                continue

            if package_name:
                REQUIRES.append(package_name)
            else:
                print("Could not import '%s'. Please make sure you have %s "
                      "installed." % (current, human_package_name))
                sys.exit(1)

test_for_imports("gtk", "pygtk", "PyGTK")
test_for_imports("dbus", "dbus-python", "python-dbus")
test_for_imports(["notify2", "pynotify"], "notify2", "pynotify or notify2")
test_for_imports("vte", None, "python-vte")

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
    long_description=read("README.rst"),
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
