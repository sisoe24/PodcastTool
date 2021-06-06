#!/usr/bin/env bash

DIR="${BASH_SOURCE%/*}"
if [[ ! -d "$DIR" ]]; then DIR="$PWD"; fi
. "$DIR/utils.sh"

function launch_ui() {
    if [[ "$OSTYPE" == 'linux-gnu'* ]]; then
        "$(current_dir)/PodcastTool"
    elif [[ "$OSTYPE" == 'darwin'* ]]; then
        /Application/PodcastTool.app/Contents/MacOS/PodcastTool
    fi
}

function main() {

    declare -a options
    options=(
        'Lancia PodcastTool'
        'Exit'
    )

    select opt in "${options[@]}"; do
        case "$opt" in
        "${options[0]}")
            launch_ui
            ;;
        esac
    done
}

if [[ -z "$*" ]]; then
    main
else
    while getopts ":l" opt; do
        case "${opt}" in
        l)
            launch_ui
            ;;
        *)
            echo 'do nothing'
            ;;
        esac
    done
fi
