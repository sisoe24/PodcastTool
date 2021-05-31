#!/bin/bash

# build linux standalone package with pyinstaller
# https://pyinstaller.readthedocs.io/en/stable/usage.html
source "$(dirname "${BASH_SOURCE[0]}")/podcasttoolrc.sh"

for dir in 'dist' 'build'; do
    if [[ -d $PACKAGE/$dir ]]; then
        rm -rf "${PACKAGE:?}/$dir"
        echo "cleaning: $dir"
    fi
done

pyinstaller src/main.py \
    --icon "$ICON" \
    --noconfirm \
    -n "$APP_NAME" \
    --add-data resources:resources
