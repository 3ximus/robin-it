#Robin It#
================================

*Version 1.0.1*

Python web crawler and TV Shows tracker to automaticly searches and gatheres torrents.

--------------------------------

##Instalation

The main dependencies are listed in the requirements.txt, and can be installed through `pip install -r requirements.txt`

You may also need python-lxml wich you can get through your package manager:
ex:

	. apt-get install python-lxml

	. pacman -S python-lxml

or through their website -> [lxml](http://lxml.de/installation.html)

then just run `python2 setup.py build`

## Usage

After building the compiled executable should be in the build directory under `robinit_console_vx.x.x`

## Changelog

**New in v1.0.1**

- Windows color support
- Fixed profile saving bug
- Compatibility fix for windows

**New in v1.0.0**

*RobinIt Console*

- Possible to build a persistent list of episodes
- Use previously built list to download episodes torrents

*TV Downloader script*

- Searches for available tv shows torrents at given a show name, quality (optional), season and episodes (optional) (Only Working for Kickass Torrents)


--------------------------------

##[Known Bugs](https://github.com/3ximus/robin-it-console/labels/bug)
