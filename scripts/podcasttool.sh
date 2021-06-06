#!/usr/bin/env bash

function __abs_path() {
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

VERSION="2.3"
APP_NAME="PodcastTool"

function current_dir() {
	current_dir="$(readlink -m "$(dirname "${BASH_SOURCE[0]}")")"
	app_path="$(dirname "$current_dir")"
	echo "$app_path"
}

function create_cmd_shortcut() {
	echo 'Creo comando per terminale...'

	local current_file
	current_file="$(basename "$BASH_SOURCE")"

	local cmd
	local cmd_path

	if [[ "$OSTYPE" == 'linux-gnu'* ]]; then
		cmd_path="/opt/$APP_NAME"
	elif [[ "$OSTYPE" == 'darwin'* ]]; then
		cmd_path="/Applications/$APP_NAME.app/Contents/Resources"
	fi

	cmd="alias podcasttool='bash $cmd_path/scripts/$current_file'"

	local bashrc
	bashrc="$HOME/.bashrc"

	if ! grep "podcasttool" "$bashrc" 1>/dev/null; then
		printf "\n%s" "$cmd" >>"$bashrc"
	else
		sed -i -E 's|alias podcasttool.*|'"$cmd"'|' "$bashrc"
	fi

	echo "Comando creato: $cmd"

}

# Create application shortcut
function create_app_shortcut() {
	echo 'Creo applicazione shortcut...'

	local file
	file="/usr/share/applications/$APP_NAME.desktop"

	if (
		sudo -s -H <<-EOF
			cat >"$file"
			[Desktop Entry]
			Version=$VERSION
			Name=$APP_NAME
			Comment=app
			Exec=/opt/$APP_NAME/$APP_NAME
			Icon=/opt/$APP_NAME/resources/images/app.png
			Terminal=false
			Type=Application
			Encoding=UTF-8
			StartupNotify=true
		EOF
	); then
		echo "Shortcut creata in app launchpad!"
	fi

}

function launch_ui() {

	if [[ "$OSTYPE" == 'linux-gnu'* ]]; then
		"$(current_dir)/$APP_NAME"
	elif [[ "$OSTYPE" == 'darwin'* ]]; then
		/Application/PodcastTool.app/Contents/MacOS/PodcastTool
	fi
}

function install() {
	sudo -s -H <<-EOF
		if [[ -d /opt/PodcastTool ]]; then
			echo 'Cancello vecchia versione...'
			rm -rf /opt/PodcastTool && echo 'Fatto'
		fi

		echo 'Installazione in corso...'
		cp -r $(current_dir) /opt/

	EOF

	create_app_shortcut
	create_cmd_shortcut

	echo 'Installazione completata'

}

function only_linux() {
	if [[ "$OSTYPE" != 'linux-gnu'* ]]; then
		echo 'Only for linux'
		main
	fi
}

function main() {

	echo "PodcastTool $VERSION"

	declare -a options
	options=(
		'Lancia PodcastTool'
		'Installa'
		'Crea CMD Shortcut'
		'Crea App Shortcut'
		'Exit'
	)

	select opt in "${options[@]}"; do
		case "$opt" in
		"${options[0]}")
			launch_ui
			;;
		"${options[1]}")
			only_linux
			install
			;;
		"${options[2]}")
			create_cmd_shortcut
			;;
		"${options[3]}")
			only_linux
			create_app_shortcut
			;;
		"Exit")
			exit 0
			;;
		*)
			main
			;;
		esac
	done
}

main
