#!/usr/bin/env bash

# PODCAST TOOL start up script for clean os

SERVER=""

if [[ -z $SERVER ]]; then

    if [[ -z $TEST_SERVER ]]; then
        echo 'need server path'
        exit
    fi

    SERVER=$TEST_SERVER
fi

SERVER_PT="$SERVER":/home/${SERVER%%@*}/Developer/PodcastTool

PT="$HOME/PodcastTool"

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
        rsync -avz --progress "$SERVER_PT"/resources/samples
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

    rsync -avz --progress "$SERVER_PT"/dist/PodcastTool_*.zip ~/Downloads
    unzip "$zip_file"

    "$PT"/PodcastTool
}

function podcasttool() {

    file="$HOME/PodcastTool/resources/scripts/podcasttool.sh"

    if [[ ! -f $file ]]; then
        echo "file doesnt exists yet. try getting the app first"
        main
    fi

    declare -a options
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

    declare -a options
    options=(
        "Get App from ubuntutest"
        "Open .desktop file"
        "Open podcasttool"
        "Get Podcasts wav samples folder"
    )

    select setup in "${options[@]}" 'Exit'; do
        case "$setup" in
        "${options[0]}")
            get_app
            ;;
        "${options[1]}")
            destkop_shortcut
            ;;
        "${options[2]}")
            podcasttool
            ;;
        "${options[3]}")
            get_podcasts_folder
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
