#!/usr/bin/env bash

DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
. "$DIR/utils.sh"

VERSION="2.3"
APP_NAME="PodcastTool"

function create_cmd_shortcut() {

	local cmd
	local cmd_path

	if [[ "$OSTYPE" == 'linux-gnu'* ]]; then
		cmd_path="/opt/$APP_NAME"
	elif [[ "$OSTYPE" == 'darwin'* ]]; then
		cmd_path="/Applications/$APP_NAME.app/Contents/Resources"
	fi

	cmd="alias podcasttool='bash $cmd_path/scripts/podcasttool.sh'"

	echo "  Creo comando per terminale... $cmd"

	local bashrc
	bashrc="$HOME/.bashrc"

	if ! grep "podcasttool" "$bashrc" 1>/dev/null; then
		printf "\n%s" "$cmd" >>"$bashrc"
	else
		sed -i -E 's|alias podcasttool.*|'"$cmd"'|' "$bashrc"
	fi

}

# Create application shortcut
function create_app_shortcut() {
	echo '  Creo applicazione shortcut in launchpad...'

	local file
	file="/usr/share/applications/$APP_NAME.desktop"

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

}
function install() {
	echo 'Installazione in corso...'
	sudo -s -H <<-EOF
		if [[ -d /opt/PodcastTool ]]; then
			echo '  Cancello vecchia versione...'
			rm -rf /opt/PodcastTool
		fi

		cp -r $(current_dir) /opt/

	EOF

	create_app_shortcut
	create_cmd_shortcut

	echo 'Installazione completata'

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
			bash "$(current_dir)/scripts/podcasttool.sh" -l
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
