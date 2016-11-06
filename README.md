#Robin It
================================

*Version 0.4*

Python GUI Application to search, track and download tvshows and movie torrents

--------------------------------

## Screenshots

![screenshot](screenshots/my_shows_screen_v1.0.png)

![screenshot](screenshots/tv_show_screen_v1.0.png)

## Instalation

Before manually installing try one of the compiled builds on the branches "releases-<arch>", if that does not work follow this:

The python version used is python2.7, i will popssibly port it to python3.5 since PyQt5 only officially supports 3.5 if i'm not mistaken. The main dependencies are listed in the requirements.txt, and can be installed through:

 `pip install -r requirements.txt`

Python bindings for Qt5 can be installed through:

ubuntu: 	`apt-get install python-qt5` or ` python-pyqt5`

arch: 		`pacman -S python2-pyqt5`

Run `python robinit_gui.py`

## Usage

Run `python robinit_gui.py`

## Changelog

**New in v1.0**

- Basic tracking system fullt implemented
    - See shows left to watch
- GUI stability and coherence improvements
- Settings menu functionality

**New in v0.5**

- Stability Improvements

**New in v0.4**

- Delete followed shows
- Mark shows, seasons or episodes as watched

**v0.3**

- Able to add shows

**v0.2**

- TVShow search function

**v0.1**

- Preliminar GUI version

--------------------------------

##Known Bugs

See [here](https://github.com/3ximus/robin-it-console/labels/bug)
