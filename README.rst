#############
PodcastTool 2
#############


NOTE
https://www.fonderiesonore.com commissioned me to build this application for a specific workflow.

Description
***********

The application will create and upload various podcast files to an online server. This version of the application brings an improvement over its predecessor by adding a GUI approach.
In addition to the visual interaction, it adds the following:

- Documented codebase.
- Error scanner for the podcast nomenclature.
- Customizable audio options for exporting.
- Multi-threaded support for faster exports.
- New interactive catalog.
- Linux, macOS, and Windows support.
- And many more.

Install on MacOS
================

Note: There is a bug on macOS Mojave 10.14.6, which would cause Tkinter to crash when the code is compiled as an application. A workaround is not to build the app and use the terminal to initiate it.


Requirements
============

The application depends on FFMPEG. FFMPEG can be installed manually or preferably via `Homebrew <https://brew.sh/>`_.

Install on Linux-Ubuntu
=======================

Create standalone
-----------------

The application depends on ``ffmpeg`` and ``xsel``.

The version of Linux on which the application is built matters. e.g., building on Ubuntu 17.10 won't work on Ubuntu 19.04 and vice-versa.
Pyinstaller is needed to compile the standalone app.


A script is provided inside the include/scripts folder to create the standalone package in the home directory.

An additional script is provided to create a .desktop file.
This will automatically create the file and place it in the /usr/share/applications folder. Once done, there will be an alias in the launchpad ready to be used.


Install manually
----------------

A script (`include/scripts/setup_app.sh`) is be provided for a quick setup, but to summarize:

- ``python3.7``
- ``python3-tk``
- ``python3-pip``
- ``libpython3.7-dev``
- ``git``
- ``ffmpeg``
- ``xsel``
        
After launching the script, a new shortcut will be created on the Desktop.

Note
====

This project has been set up using PyScaffold 3.1. For details and usage
information on PyScaffold see https://pyscaffold.org/.
