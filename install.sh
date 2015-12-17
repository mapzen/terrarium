#!/bin/bash

os=$(uname)
arq=$(uname -m)

apps_osx="python freetype pyqt opencv"
apps_linux_rpi="libgeos++ python-dev python-opencv"
apps_linux_ubuntu="libgeos++ python-devel python-opencv"
python_global="virtualenv virtualenvwrapper" 
python_base_modules="scipy pil numpy request shapely"

#   Install Applications
#   ===============================================================
if [ $os == "Linux" ]; then

    # on Debian Linux distributions
    sudo apt-get update
    sudo apt-get upgrade

    # on RaspberryPi
    if [ $arq == "armv7l" ]; then
        sudo apt-get install $apps_linux_rpi
    else
        sudo apt-get install $apps_linux_ubuntu
    fi

    # Install Python need files
    if [ ! -e /usr/local/bin/pip ]; then
        wget https://bootstrap.pypa.io/get-pip.py
        sudo python get-pip.py
        rm get-pip.py
        sudo pip install $python_global
    fi

elif [ $os == "Darwin" ]; then
    
    # ON MacOX 
    
    if [ ! -e /usr/local/bin/brew ]; then
        ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    fi

    brew update
    brew upgrade
    brew install $apps_osx

    if [ ! -e /usr/local/bin/pip ]; then
        pip install $python_global
    fi
fi

## Finish instalation of python modules under base virtual enviroment
source ~/.zshrc
if [ ! -d ~/.virtualenvs/base ]; then
    mkvirtualenv base
    workon base
    pip install $python_base_modules
fi
