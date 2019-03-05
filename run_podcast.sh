#!/bin/bash

# desktop app will call this script to launch the gui

#resize terminal window 
printf '\e[8;30;65t'

DIR="$( dirname ${BASH_SOURCE[0]} )"

UPDATE=$( cd $DIR && git pull )
if [ "$UPDATE" "==" "Already up-to-date." ]; then
  echo "Already up to date"
else
  echo "Update in progress.. this should take just a second"
  xdg-open $DIR/CHANGELOG.rst
fi

APP=$DIR/src/gui/main_gui.py
LAUNCH_APP=$( which python3.7 ) $APP

echo $LAUNCH_APP >> FATAL_ERROR.txt
