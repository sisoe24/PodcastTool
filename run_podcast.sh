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
  gedit $DIR/CHANGELOG.rst
fi

APP=$DIR/src/gui/main_gui.py
# create log directory if doesnt already exists
! [ -d $DIR/log ] && mkdir $DIR/log

# catch fatal error that won't start the app
# if file exists already from last session then delete
ERROR_LOG=$DIR/log/FATAL_ERROR.txt
[ -f $ERROR_LOG ] && rm -f $ERROR_LOG

$( which python3.7 ) $APP 2> $ERROR_LOG

if [ -s $ERROR_LOG ]; then
  sed -i '1s/^/FATAL ERROR\n\n' $ERROR_LOG
  gedit $ERROR_LOG
fi
