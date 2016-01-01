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

##TV API - get show information (latest v1.2)##

Searches thetvdb.com and gathers TV show information

*Usage*:

- Follow example usage at the end of the api

*General Changelog*:

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

##TODO##

**v1.3**: (Traking System)

- Tv Show tracking

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

- Custom tvdb_api

**v2.2**:

- Multiple devices

**v2.3**:

- Multiple device persistence

###OTHER TODO###

- Add a torrent url and magnet to an episode / movie so that it gets saved

*Notes* : Use Kickass API instead of parsing when/if available

--------------------------------

##Known Limitations##

--------------------------------
##Known Bugs##
