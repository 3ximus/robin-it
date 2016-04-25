#Web Crawler#
================================

*Version 1.3*

Python web crawler to automaticly search and gather web resources.

--------------------------------

##TV Downloader - download tv shows (latest v1.1)##

Searches for available tv shows torrents at given a show name, quality (optional), season and episodes (optional)

*Usage*:

- `$ ./tv_downloader.py`
- If Quality left blank defaults to 720p
- If Episodes left blank defaults to 10 episodes `range(11)[1:]` , in the

##TV API - get show information (latest v1.3)##

Searches thetvdb.com and gathers TV show information

*Usage*:

- Follow example usage at the end of the api

##RobinIt API - User Information and Content (latest v1.3)##

Stores user information such as following shows and movies (movies not added as of v1.3)
It can be made persistent saving its state to a file and loading it back (loading and saving must be called manually anytime you want the action to take place)

##RobinIt Console [CLI] - Track/Manage User Information and Contnet (latest v1.3)##

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

or through their website -> [lxml](http://lxml.de/installation.html)

###TODO###

- Maintain a version control over tv_shows.py classes in order to load correctly, same for user content ( possibly later add multiple ways to convert user saved data to current releases )

- Add a torrent url and magnet to an episode / movie so that it gets saved

- Get apikey for thetvdb API for the user (prompt user to register the website) - later implementation of this is to get a login screen that gets the apikey)

- Use `https://pirateproxy.tv/` as a backup for when kickass is missing torrents

*Notes* : Use Kickass API instead of parsing when/if available

--------------------------------

##Known Bugs##