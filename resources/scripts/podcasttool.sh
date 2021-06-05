#!/usr/bin/env bash

VERSION="2.3"
APP_NAME="PodcastTool"

SCRIPTS_DIR="$(readlink -m "$(dirname "${BASH_SOURCE[0]}")")"
RESOURCES="$(dirname "$SCRIPTS_DIR")"

function create_alias() {
	local bashrc
	bashrc="$HOME/.bashrc"

	local current_file
	current_file="$(basename "$BASH_SOURCE")"

	local cmd
	cmd="alias podcasttool='bash $RESOURCES/scripts/podcasttool.sh'"

	if ! grep "podcasttool" "$bashrc" 1>/dev/null; then
		printf "\n%s" "$cmd" >>"$bashrc"
	else
		sed -i -E 's|alias podcasttool.*|'"$cmd"'|' $file
	fi
}

# Create application shortcut
function create_shortcut() {

	if [[ $(/usr/bin/id -u) -ne 0 ]]; then
		echo "This action requires Root access."
	fi

	local file
	file="/usr/share/applications/$APP_NAME.desktop"

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

	echo "Shortcut creata in app launchpad!"
}

function launch_ui() {

	if [[ "$OSTYPE" == 'linux-gnu'* ]]; then

		declare -a files

		while IFS= read -r -d '' file; do
			files+=("$file")
		done < <(find . -type f -name "PodcastTool" -print0)

		if [[ ${#files[@]} -gt 1 ]]; then
			select file in "${files[@]}"; do
				./"$file"
			done
		else
			./"${files[0]}"
		fi

	elif [[ "$OSTYPE" == 'darwin'* ]]; then
		/Application/PodcastTool.app/Contents/MacOS/PodcastTool
	fi
}

function main() {
	declare -a options

	options=(
		'Lancia PodcastTool'
		'Crea App Shortcut'
		'Crea CMD Shortcut'
		'Exit'
	)

	select opt in "${options[@]}"; do
		case "$opt" in
		"${options[0]}")
			launch_ui
			;;
		"${options[1]}")
			create_shortcut
			;;
		"${options[2]}")
			create_alias
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
