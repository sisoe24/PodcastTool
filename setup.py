"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['src/main.py']
DATA_FILES = ["include", "docs", "log", "archive"]
OPTIONS = {
    "iconfile": "include/img/app.icns",
    "packages": ["podcasttool"],
}

setup(
    app=APP,
    name="PodcastTool",
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
