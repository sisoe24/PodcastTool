#!/bin/bash

if [[ "$OSTYPE" != 'linux-gnu'* ]]; then
    echo 'Only for Linux'
    exit
fi

CURRENT_DIR="$(dirname "${BASH_SOURCE[0]}")"
RESOURCES="$(dirname "$CURRENT_DIR")"
PACKAGE="$(dirname "$RESOURCES")"
ICON="$RESOURCES/images/app.png"
APP_NAME="PodcastTool"
