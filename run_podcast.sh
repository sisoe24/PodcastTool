#!/bin/bash

# desktop app will call this script to launch the gui

DIR="$( dirname ${BASH_SOURCE[0]} )"

UPDATE=$( cd $DIR && git pull )
if [ "$UPDATE" "==" "Already up-to-date." ]; then
  echo "Already up to date"
else
  echo "Updating in progress.. thi should take a second"
  xdg-open $DIR/CHANGELOG.rst
fi
APP=$DIR/src/gui/main_gui.py
$( which python3.7 ) $APP

