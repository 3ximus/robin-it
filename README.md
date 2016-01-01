#Web Crawler#
================================

*MAIN README FILE

Python web crawler to automaticly search and gather web resources.

--------------------------------

##TV Show Search Engine v1.1##

Searches for available tv shows given keyword, quality (optional), season and episodeS (optional)

*Usage*:

	. `$ ./tv_crawler.py`
	. If Quality left blank defaults to 720p
	. If Episodes left blank defaults to 10 episodes `range(11)[1:]`

##TV API - get show information v1.2##

Searches thetvdb.com nd gathers TV show information

*Usage*:
	
	. Follow example usage at the end of the api
	

*Changelog*:

**v1.2**: (Info Display)

	- Get TV show info (DONE)

**v1.1**: (Speed and Usability Upgrades)

	- Implement a beautiful soup parser (DONE)
	- Implement custom parser (DISCONTINUED)
	- Remove the get download links and use the search algorithm to retrive the magnets and torrent links (DONE)
	- Implement `parse_page_links_2` to use with any parser. Also make it receive content instead of making it get the page (DONE)

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
