#!/bin/bash

if [[ "$OSTYPE" != 'linux-gnu'* ]]; then
    echo 'Only for Linux'
    exit
fi

SCRIPTS_DIR="$(readlink -m "$(dirname "${BASH_SOURCE[0]}")")"

RESOURCES="$(dirname "$SCRIPTS_DIR")"
PACKAGE="$(dirname "$RESOURCES")"

ICON="$RESOURCES/images/app.png"

APP_NAME="PodcastTool"
