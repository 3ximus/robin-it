#Robin It#
================================

*Version 1.0.0*

Python web crawler and TV Shows tracker to automaticly searches and gatheres torrents.

--------------------------------

## Usage

After building the compiled executable should be in the build directory under `robinit_console_vx.x.x'


##TV Downloader - download tv shows (latest v1.0.0)##

Searches for available tv shows torrents at given a show name, quality (optional), season and episodes (optional)

*Usage*:

- `$ ./tv_downloader.py`
- If Quality left blank defaults to 720p
- If Episodes left blank defaults to 10 episodes `range(11)[1:]` , in the

##TV API - get show information (latest v1.0.0)##

Searches thetvdb.com and gathers TV show information

##RobinIt API - User Information and Content (latest v1.0.0)##

Stores user information such as following shows and movies (movies not added as of v1.0.0)
It can be made persistent saving its state to a file and loading it back (loading and saving must be called manually anytime you want the action to take place)

##RobinIt Console [CLI] - Track/Manage User Information and Content (latest v1.0.0)##

In this version its is possible to add and remove tv shows to following list, list them and checks wich episodes are unwatched
It is not possible with this CLI to set the watched states os episodes/season/shows, it may be added in the future in the CLI version

*Usage*:

- `$ ./robinit_console.py`
- Type username, if save file exists it will try to load it ( default location at ./user/ directory )
- Follow menu interaction and try not to blow it up


##Instalation

The main dependencies are listed in the requirements.txt, and can be installed through `pip install -r requirements.txt`

You may also need python-lxml wich you can get through your package manager:
ex:

	. apt-get install python-lxml

	. pacman -S python-lxml

or through their website -> [lxml](http://lxml.de/installation.html)

then just run `python2 setup.py build`

--------------------------------

##Known Bugs##
