#!/usr/bin/env bash

VERSION="2.3"
APP_NAME="PodcastTool"

SCRIPTS_DIR="$(dirname "${BASH_SOURCE[0]}")"
RESOURCES="$(dirname "$SCRIPTS_DIR")"

function create_cmd_shortcut() {
	local bashrc
	bashrc="$HOME/.bashrc"

	local current_file
	current_file="$(basename "$BASH_SOURCE")"

	local cmd
	cmd="alias podcasttool='bash $RESOURCES/scripts/$current_file'"

	if ! grep "podcasttool" "$bashrc" 1>/dev/null; then
		printf "\n%s" "$cmd" >>"$bashrc"
	else
		sed -i -E 's|alias podcasttool.*|'"$cmd"'|' "$bashrc"
	fi

	echo "Done"
}

# Create application shortcut
function create_app_shortcut() {

	if [[ $(/usr/bin/id -u) -ne 0 ]]; then
		echo "This action requires Root access."
	fi

	local file
	file="/usr/share/applications/$APP_NAME.desktop"

	if (
		sudo -s -H <<-EOF
			cat >"$file"
			[Desktop Entry]
			Version=$VERSION
			Name=$APP_NAME
			Comment=app
			Exec=$HOME/$APP_NAME/$APP_NAME
			Icon=$RESOURCES/images/app.png
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

		declare -a files

		while IFS= read -r -d '' file; do
			files+=("$file")
		done < <(find $HOME -type f -name "PodcastTool" -print0 2>/dev/null)

		if [[ ${#files[@]} -gt 1 ]]; then
			select file in "${files[@]}"; do
				case "$file" in
				"Back")
					launch_ui
					;;
				*)
					if [[ -n $file ]]; then
						"$file"
					fi
					;;
				esac
			done
		else
			"${files[0]}"
		fi

	elif [[ "$OSTYPE" == 'darwin'* ]]; then
		/Application/PodcastTool.app/Contents/MacOS/PodcastTool
	fi
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
			create_app_shortcut
			;;
		"${options[2]}")
			only_linux
			create_cmd_shortcut
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
