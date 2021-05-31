#!/usr/bin/env bash

# if [[ "$OSTYPE" != 'linux-gnu'* ]]; then
# 	echo 'Only for Linux'
# 	exit
# fi

# SCRIPTS_DIR="$(readlink -m "$(dirname "${BASH_SOURCE[0]}")")"

RESOURCES="$(dirname "$SCRIPTS_DIR")"
PACKAGE="$(dirname "$RESOURCES")"

ICON="$RESOURCES/images/app.png"

APP_NAME="PodcastTool"

# build linux standalone package with pyinstaller
# https://pyinstaller.readthedocs.io/en/stable/usage.html
function build_linux() {
	if [[ -z "$VIRTUAL_ENV" ]]; then
		echo 'Not inside virtual einvornment?'
		exit 1
	fi

	echo "Creating Build..."

	exit
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

}

# Create application shortcut
function create_shortcut() {

	if [[ $(/usr/bin/id -u) -ne 0 ]]; then
		echo "This script requires Root access. Try with sudo"
		exit 1
	fi

	echo 'Create shortcut'

	cat <<-END >>/usr/share/applications/$APP_NAME.desktop
		[Desktop Entry]
		Version=2.3
		Name=$APP_NAME
		Comment=app
		Exec=$HOME/$APP_NAME/$APP_NAME
		Icon=$ICON
		Terminal=false
		Type=Application
		Encoding=UTF-8
		StartupNotify=true" 
	END

	echo "Shortcut create in app launchpad!"
}

function helper() {
	_tab=$'\t'
	cat <<-END
		Usage: $(basename "$0") [-h] [-s] [-b] 
		Optional args:
		-h  ${_tab} Display this help message.
		-s  ${_tab} Create Application Shortcut.
		-b  ${_tab} Build Linux Application
	END
	exit 1
}

while getopts "h:s:b" opt; do
	case ${opt} in
	h)
		helper
		;;
	s)
		create_shortcut
		;;
	b)
		build_linux
		;;
	\?)
		echo "Invalid option: $OPTARG" 1>&2
		helper
		;;
	*)
		echo "Unkown options: $OPTARG"
		helper
		;;
	esac
done
