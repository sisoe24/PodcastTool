#!/usr/bin/env bash

# PODCAST TOOL start up script for clean os

SERVER=""

if [[ -z $SERVER ]]; then
    echo "Need server ip address"
    exit 1
fi

PT="$HOME/PodcastTool"
DPT="$HOME/Developer/PodcastTool"

alias cdpt='cd $PT'
alias pt='$PT/PodcastTool'

function __setup_utility() {
    echo 'Install utility Applications'
    # snap: neovim
    # apt: gnome-tweak-tool dolphin terminator
    #      for virtual box: build-essentials gcc make perl dkms
    # get .vimrc/init.vim
}

function get_podcasts_folder() {
    local podcasts
    podcasts="$HOME"/Desktop/Podcast

    if [[ ! -d $podcasts ]]; then
        rsync -avz --progress "$SERVER:$DPT/resources/samples"
    fi
}

function get_app() {
    local zip_file
    zip_file="$HOME/Downloads/PodcastTool_*.zip"

    for i in "$zip_file" "$PT"; do

        if [[ -d $i || -f $i ]]; then
            echo "Deleting: $i"
            rm -rf "$i"
        fi
    done

    rsync -avz --progress "$SERVER:$DPT"/dist/PodcastTool*.zip ~/Downloads
    unzip "$zip_file"

    "$HOME"/PodcastTool/PodcastTool
}

function _podcasttool() {

    file="$HOME/PodcastTool/resources/scripts/podcasttool.sh"

    if [[ ! -f $file ]]; then
        echo "file doesnt exists yet. try getting the app first"
        exit 0
    fi

    local options -a
    options=('Edit' 'Run' 'Build' 'Create Desktop shortcut')

    select mode in "${options[@]}"; do
        case "$mode" in
        "${options[0]}")
            vi "$file"
            ;;
        "${options[1]}")
            bash "$file"
            ;;
        "${options[3]}")
            bash "$file" -b
            ;;
        "${options[4]}")
            bash "$file" -c
            ;;
        esac
    done
}

function destkop_shortcut() {
    local file
    file=/usr/share/applications/PodcastTool.desktop

    if [[ -f $file ]]; then
        sudo vi "$file"
    else
        echo 'File doesnt exists yet'
    fi
}

function main() {

    local options -a
    options=(
        "Get App from ubuntutest"
        "Open .desktop file"
        "Open podcasttool"
        "Get Podcast folder"
    )

    select setup in "${options[@]}" 'Exit'; do
        case "$setup" in
        "${options[0]}")
            get_app
            ;;
        "${options[1]}") ;;

        \
            "${options[2]}")
            _podcasttool
            ;;
        "${options[3]}")
            get_podcasts_folder
            ;;
        "Exit")
            exit 0
            ;;
        *)
            echo "do something else"
            exit 0
            ;;
        esac
    done
}

main
