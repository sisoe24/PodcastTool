#!/bin/bash

# desktop app will call this script to launch the gui

DIR="$( dirname ${BASH_SOURCE[0]} )"
APP=$DIR/src/gui/main_gui1.py
$( which python3.7 ) $APP

