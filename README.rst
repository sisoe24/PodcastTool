#############
PodcastTool 2
#############


A tool I made for https://www.fonderiesonore.com.

This tool is needed for parsing and uploading podcast files to their platform.
PodcasTool 2 is based on the original PodcastTool, which was written in PHP.
It improves on its predecessor by adding a GUI approach. In addition
it to the visual interaction, it does also improve on the following topics:

* Error helper system.
* Multi threading operation.
* Customizable audio options for user.
* Ability to create/modifiy the custom audio.
* Linux, macOS and Windows support.

Description
***********

The use of this application is made for a specific workflow, therefore it not usable
for other purposes.

Supported platform
##################

* macOS 13x, 15x
  * macOS Mojave 14x has a bug where Tkinter app cannot be compiled but the app can still launched from the terminal
* Ubuntu >17.10

Dependencies
############
https://ffbinaries.com/downloads
If standalone app is used technically the app only requires __ffmpeg__ to be on the system, but if is not, application will fallback on an included ffmpeg binary. this should work in most cases.

Build app
*********

Both platform need to have their virtual envoirment setup. All Python3x version should work, but currently it has been compiled with `3.9.5` on both platform. 

Application requires Python to have the Tkinter module installed and on neither of the platform is it.

macOS
#####

``py2app`` is required.

* Install Tkinter with on of the way:

  * Via `Hombrew <https://brew.sh/>`_: ``brew install python-tk@3.9``
  * Officialy from `Python website <https://www.python.org/>`_.

* Once inside virtual environment launch the _setup.py_: ``python setup.py py2app``
* Application file *PodcastTool.app* will be inside the *dist* folder.

Linux Ubuntu
############

``pyinstaller`` is required

  The `TkDocs website <https://tkdocs.com/tutorial/install.html/>`_ has all the information about all platform installation

To install python with tkinter there are a few ways depending on the distro version and which Python you are targeting. 

The easiest way is to install Python with Tk via the package manager, but this will usually limit the version of Python you can download, especially if you are on an outdated OS:

  ``sudo apt install python3-tk``

Alternativly Python could also be compiled from source and build with tk

1. Download Python source code from `Python website <https://www.python.org/>`_.
2. Download Tcl from https://www.activestate.com/products/tcl/
    * or via the package manager `sudo apt install tk8.6-dev`
3. Build Python 
    * If tk is installed via the package manger, path should differ)
    * `--enable-shared` argument is for `pyinstaller`
  
code:: bash

  cd python-3x
  ./configure --with-tcltk-includes='-I/opt/ActiveTcl-8.6/include' --with-tcltk-libs='/opt/ActiveTcl-8.6/lib/libtcl8.6.so /opt/ActiveTcl-8.6/lib/libtk8.6.so' --enable-shared LDFLAGS='-Wl,-rpath /usr/local/lib'
  sudo make
  sudo make install # or altinstall to not override  current version

1. Launch python and check for tk: `import tkinter`. If an error occurs, some packages might still be missing:
  `sudo apt install build-essential libssl-dev libffi-dev libx11-dev python3-dev`
5. From inside the virtual environment, launch the build script: `bash resources/scripts/build_linux.sh`
6. Application will be build inside the _dist_ folder.
7. Optional. A shortcut desktop icon can be created with the included scripts: `sudo bash resources/scripts/build_desktop.sh`

