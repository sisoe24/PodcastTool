#!/usr/bin/env bash

if [[ -z "$VIRTUAL_ENV" ]]; then
	echo 'Not inside virtual einvornment?'
	exit 1
fi

function abs_path() {
	local current_dir
	current_dir="$(dirname "${BASH_SOURCE[0]}")"

	# clean pwd if calling it from root so we can avoid conditionals
	current_dir=${current_dir##$(pwd)}

	# this will create double slash in some occasions
	current_dir="$(pwd)/$current_dir"
	current_dir=${current_dir/\/\//\/}

	if [[ -d $current_dir ]]; then
		echo "$current_dir"
	else
		echo "$current_dir: not a valid path?"
	fi

}

APP_NAME="PodcastTool"
VERSION="2.3"
PACKAGE=$(abs_path)

function clean_dirs() {
	for dir in 'dist' 'build'; do
		if [[ -d $dir ]]; then
			rm -rf "$dir"
			echo "cleaning: $dir"
		fi
	done
}

function zip_app() {

	if [[ -n $1 && $1 == 'z' ]]; then

		local platform
		local app
		app='PodcastTool'

		if [[ "$OSTYPE" == 'linux-gnu'* ]]; then
			platform='ubuntu1710'
		elif [[ "$OSTYPE" == 'darwin'* ]]; then
			app="$app.app"
			platform='macOS136'
		fi

		(cd dist && zip -r PodcastTool_"$VERSION"_"$platform".zip "$app")
	fi
}

# build linux standalone package with pyinstaller
# https://pyinstaller.readthedocs.io/en/stable/usage.html
function build_linux() {

	echo "Creating Build for Linux..."
	clean_dirs

	pyinstaller src/main.py \
		--icon "$PACKAGE/resources/images/app.png" \
		--noconfirm \
		--paths src \
		-n "$APP_NAME" \
		--add-data resources:resources \
		--add-data scripts:scripts \

	zip_app "$1"

}

function build_mac() {
	echo "Creating Build for Mac..."
	clean_dirs

	python setup.py py2app

	zip_app "$1"

}

function helper() {
	_tab=$'\t'
	cat <<-END
		Usage: bash $(basename "$0") [-h] [-m] [-l]
		Optional args:
		-h  ${_tab} Display this help message.
		-m  ${_tab} Build Mac Application
		-l  ${_tab} Build Linux Application
	END
	exit 1
}

function main() {
	declare -a options
	options=(
		'Build Mac'
		'Build Linux'
	)
}

while getopts "h:ml" opt; do
	case ${opt} in
	h)
		helper
		;;
	m)
		build_mac "$2"
		;;
	l)
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
