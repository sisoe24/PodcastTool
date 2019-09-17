#!/bin/bash

# create desktop shortcut app for linux

if [[ $(/usr/bin/id -u) -ne 0 ]]; then
    echo "This script requires Root access. Try with sudo"
    exit
fi

INCLUDE_DIR="$( dirname $( dirname ${BASH_SOURCE[0]} ) )"

echo "[Desktop Entry]
Version=2.2
Name=PodcastTool
Comment=app
Exec=$HOME/PodcastTool/PodcastTool
Icon=$HOME/PodcastTool/include/img/app.png
Terminal=false
Type=Application
Encoding=UTF-8
StartupNotify=true" > /usr/share/applications/PodcastTool.desktop

echo "shortcut app create in app launchpad!"