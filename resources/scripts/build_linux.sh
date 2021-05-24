#!/bin/bash
 
# build linux standalone package with pyinstaller
# https://pyinstaller.readthedocs.io/en/stable/usage.html

pyinstaller src/main.py \
    --distpath "$HOME" \
    --icon resources/images/app.png \
    --noconfirm \
    -n PodcastTool \
    --add-data resources:resources \
