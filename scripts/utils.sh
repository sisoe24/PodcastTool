#!/usr/bin/env bash

function current_dir() {
    current_dir="$(readlink -m "$(dirname "${BASH_SOURCE[0]}")")"
    app_path="$(dirname "$current_dir")"
    echo "$app_path"
}

function only_linux() {
    if [[ "$OSTYPE" != 'linux-gnu'* ]]; then
        echo 'Only for linux'
        main
    fi
}
