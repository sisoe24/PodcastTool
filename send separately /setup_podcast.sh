#!/bin/bash

# setup file for PodcastTool 2 design for user with no experience


# install packages
PACKAGES=("python3.7" "python3-tk" "python3-pip" "libpython3.7-dev" "git" "ffmpeg")

for i in ${PACKAGES[@]}; do
  sudo apt install $i -y
  echo "$i installato" >> virgil_log.txt
done

# update apt
sudo apt update

# write log check to see if has installed all
function write_log() {
  if [ $? "!=" 0]; then
    echo "$1 non riuscito" >> virgil_log.txt
  else
    echo "$1 riuscito" >> virgil_log.txt
  fi
}


# Foldes vars
DEST_DIR="Rinominatore"
VIRGIL_FOLDER="virgil_scripts"

# download podcast tool
git clone https://github.com/sisoe24/$DEST_DIR ~/$VIRGIL_FOLDER/$DEST_DIR
write_log "git clone"

# install python packages requirements
# not sure if I need pip3 or pip
python3.7 -m pip install -r ~/$VIRGIL_FOLDER/$DEST_DIR/requirements.txt
write_log "python3.7 pip install requirements"

# aliases
echo "alias cd_podcast='cd ~/$VIRGIL_FOLDER/$DEST_DIR'" >> ~/.bashrc 
write_log "alias cd_podcast"

echo "alias update_podcast='cd ~/$VIRGIL_FOLDER/$DEST_DIR && git pull && cd'" >> ~/.bashrc
write_log "alias update_podcast"

# creating desktop launchger
echo "[Desktop Entry]
Version=2.0
Name=PT2
Comment=ciao
Exec=$HOME/$VIRGIL_FOLDER/$DEST_DIR/run_podcast.sh
Icon=$HOME/$VIRGIL_FOLDER/$DEST_DIR/src/gui/img/gui/5_megaphone.png
Terminal=true
Type=Application
Encoding=UTF-8
StartupNotify=true" > $HOME/Scrivania/PT2.desktop
write_log "desktop launcher"


# giving exectuable permissions 
chmod +x $HOME/Scrivania/PT2.desktop
write_log "chmod +x desktop app"
chmod +x $HOME/$VIRGIL_FOLDER/$DEST_DIR/run_podcast.sh
write_log "chmod +x run_podcast.sh"

source ~/.bashrc
write_log "source"