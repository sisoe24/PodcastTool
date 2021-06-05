#!/usr/bin/env bash

if [[ -z "$VIRTUAL_ENV" ]]; then
	echo 'Not inside virtual einvornment?'
	exit 1
fi

APP_NAME="PodcastTool"

SCRIPTS_DIR="$(readlink -m "$(dirname "${BASH_SOURCE[0]}")")"
RESOURCES="$(dirname "$SCRIPTS_DIR")"
# build linux standalone package with pyinstaller
# https://pyinstaller.readthedocs.io/en/stable/usage.html
function build_linux() {

	echo "Creating Build..."

	local package
	package="$(dirname "$RESOURCES")"

	for dir in 'dist' 'build'; do
		if [[ -d $package/$dir ]]; then
			rm -rf "${package:?}/$dir"
			echo "cleaning: $dir"
		fi
	done

	pyinstaller src/main.py \
		--icon "$RESOURCES/images/app.png" \
		--noconfirm \
		--paths src \
		-n "$APP_NAME" \
		--add-data resources:resources

	if [[ -n $1 && $1 == 'z' ]]; then
		(cd dist && zip -r PodcastTool.zip PodcastTool)
	fi

}

function helper() {
	_tab=$'\t'
	cat <<-END
		Usage: bash $(basename "$0") [-h] [-s] [-b]
		Optional args:
		-h  ${_tab} Display this help message.
		-c  ${_tab} Create Application Shortcut.
		-b  ${_tab} Build Linux Application
	END
	exit 1
}

while getopts "h:cbs" opt; do
	case ${opt} in
	h)
		helper
		;;
	c)
		echo "do something"
		;;
	b)
		build_linux "$2"
		;;
	\?)
		echo "Invalid option: $OPTARG" 1>&2
		helper
		;;
	*)
		echo "Unkown options: $OPTARG" 1>&2
		helper
		;;
	esac
done

if [[ -z "$*" ]]; then
	helper
fi
