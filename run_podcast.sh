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
# catch fatal error that won't start the app
ERROR_LOG=$DIR/log/FATAL_ERROR.txt
$( which python3.7 ) $APP 2> $ERROR_LOG

if [ -s $ERROR_LOG ]; then
  sed -i '1s/^/FATAL ERROR\n\n' $ERROR_LOG
  gedit $ERROR_LOG
else
