#Web Crawler#
================================

*MAIN README FILE

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

##RobinIt API - User Information and Contnet (latest v1.3)##

Stores user information such as following shows and movies (movies not added as of v1.3)
It can be made persistent saving its state to a file and loading it back (loading and saving must be called manually anytime you want the action to take place)

##RobinIt Console [CLI] - Track/Manage User Information and Contnet (latest v1.3)##

In this version its is possible to add and remove tv shows to following list, list them and checks wich episodes are unwatched
It is not possible with this CLI to set the watched states os episodes/season/shows, it may be added in the future in the CLI version

*Usage*:

- `$ ./robinit_console.py`
- Type username, if save file exists it will try to load it ( default location at ./user/ directory )
- Follow menu interaction and try not to blow it up

---------------------

*General Changelog*:

**v1.3**: (Traking System)

- Tv Show tracking system system
- *API* Persistent User Status
- *API* Watched / unwatched states for tv shows
- *API* Possible to generate a tv show header build if needed for less cluttering or faster loads (only contain basic info and nothing about seasons/episodes) 

**v1.2**: (Info Display)

- *API*: Get TV show info (DONE)

**v1.1**: (Speed and Usability Upgrades)

- New Search results console display
- usage is similar to v1.0
- *API*: Use beautiful soup parser to improve the content gathrered from the web page (DONE)
- *API*: Implement custom parser (DISCONTINUED)
- *API*: Remove the get download links and use the parse algorithm to retrive the magnets and torrent links (DONE)
- *API*: Function `parse_page_links_2` to use with any parser. Also make it receive content instead of making it get the page (DONE)

**v1.0**: (First Run)

- Basic Search and Download functionality


*Multiprocess Test version on another branch*

--------------------------------

##Other tools##

Search torrents

List url from page

Benchmark Page parsers

--------------------------------

##FUTURE##

**v1.4**: (Big Release)

- Incorporate Traking with Search/Download engine

**v1.5**: (Movies)

- Add Movie info gathering

**v1.6**: (Schedule/Wait-release System)

- Add a movie schedule system to allow movie releases to be notified

**v1.7**: (Major Release)

- Incorporate movie schedule with download feature to download followed movie releases

**v2.0**:

- Implement GUI

**v2.1**:

- Custom tvdb_api gatherer

**v2.2**:

- Multiple devices

**v2.3**:

- Multiple device persistence

**v3.0**

- Add Games!

###TODO###

- Maintain a version control over tv_shows.py classes in order to load correctly, same for user content ( possibly later add multiple ways to convert user saved data to current releases )
- Add a torrent url and magnet to an episode / movie so that it gets saved
- Get apikey for thetvdb API for the user (prompt user to register the website) - later implementation of this is to get a login screen that gets the apikey)

*Notes* : Use Kickass API instead of parsing when/if available

--------------------------------

##Known Limitations##

--------------------------------
##Known Bugs##
