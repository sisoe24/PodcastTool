#!/bin/bash
source "$(dirname "${BASH_SOURCE[0]}")/podcasttoolrc.sh"

# create desktop shortcut app for linux

if [[ $(/usr/bin/id -u) -ne 0 ]]; then
    echo "This script requires Root access. Try with sudo"
    exit
fi

echo "[Desktop Entry]
Version=2.3
Name=$APP_NAME
Comment=app
Exec=$HOME/$APP_NAME/$APP_NAME
Icon=$ICON
Terminal=false
Type=Application
Encoding=UTF-8
StartupNotify=true" >/usr/share/applications/$APP_NAME.desktop

echo "shortcut app create in app launchpad!"
