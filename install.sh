#!/bin/sh

deps="python-gtk2 python-dbus python-vte python-notify python-pip"

# Colour escapes
# Source: http://stackoverflow.com/a/20983251/435253
textreset=$(tput sgr0) # reset the foreground colour
red=$(tput setaf 1)
green=$(tput setaf 2)
yellow=$(tput setaf 3)

die() {
    echo "-------------------------------------------------------------------------------"
    echo "${red}ERROR:" "$@" "${textreset}"
    echo "-------------------------------------------------------------------------------"
    exit 1
}

is_installed() { type "$1" 1>/dev/null 2>&1; return $?; }

# Make sure we've got the right working directory
# TODO: Also resolve symlinks just to play it safe
cd "$(dirname "$0")"

# Check if we were double-clicked and re-run self in a terminal
if [ ! -t 0 ]; then
    exec xterm -hold -e "$0" "$@"
fi

is_installed lgogdownloader || die "lgogd_uri requires lgogdownloader but it isn't in your \$PATH. Please correct the problem and re-run install.sh."
is_installed sudo || die "This script requires sudo to elevate privileges."

if is_installed apt-get; then
    echo "Ensuring dependencies are installed (requires root)..."
    # shellcheck disable=SC2086
    sudo apt-get install $deps || die "Failed to install dependencies. Exiting."
else
    echo "${yellow}You don't have apt-get. If this script fails or lgogd_uri doesn't run, please install these dependencies and try again:"
    echo "    $deps${textreset}"
fi

is_installed pip || die "Missing pip, which is required for installing with support for uninstall. Exiting."
is_installed update-desktop-database || die "Missing update-desktop-database, which is required for adding a URI handler. Please install desktop-file-utils."
is_installed xdg-mime || die "Missing xdg-mime, which is required for setting lgogd_uri as default handler for gogdownloader:// URIs. Please install xdg-utils."

echo "Installing lgogd_uri system-wide with support for uninstallation (requires root)..."
sudo pip install --force-reinstall . || die "Failed to install lgogd_uri system-wide. Exiting."
# Or `sudo ./setup.py install` if you don't need to uninstall

echo "Updating mimetype handler database (requires root)..."
sudo update-desktop-database || die "Failed to update mimetype handler database. Exiting."

echo "Setting lgogd_uri as default handler for gogdownloader:// for your user..."
xdg-mime default lgogd_uri.desktop x-scheme-handler/gogdownloader || die "Failed to set lgogd_uri as default gogdownloader:// handler"

echo
if is_installed apt-get; then
    echo "${green}Ok, gogdownloader:// URLs should now Just Work(tm) after you restart your browser. :)${textreset}"
else
    echo "${yellow}lgogd_uri is installed but you may have to manually install the dependencies mentioned above before it will work."
fi
