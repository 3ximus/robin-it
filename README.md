#Web Crawler#
================================

*MAIN README FILE

Python web crawler to automaticly search and gather web resources.

--------------------------------

##TV Show Search Engine v1.0.1##

Searches for available tv shows given keyword, quality (optional), season and episodeS (optional)

Usage:

	. `$ ./tv_crawler.py`
	. If Quality left blank defaults to 720p
	. If Episodes left blank defaults to 10 episodes `range(11)[1:]`
*Multiprocess Test version on another branch*

--------------------------------

##Other tools##

Search torrents

List url from page

Benchmark Page parsers

--------------------------------

##TODO##

###TV SHOWS:###

v1.1: (Speed and Usability Upgrades)

	- Implement a beautiful soup parser (DONE)
	- Implement custom parser (DISCONTINUED)
	- Remove the get download links and use the search algorithm to retrive the magnets and torrent links
	- Implement `parse_page_links_2` to use with any parser. Also make it receive content instead of making it get the page (DONE)

v1.2: (Info Display)

	- Get TV show info from a web page

v1.3: (Traking System)

	- Tv Show tracking 

v1.4: (Big Release)

	- Incorporate Traking with Search/Download engine

v2.0:
	- Implement GUI

###MOVIES###

--------------------------------

##Known Limitations##

- `build_search_url` and `get_download_links` only work for KICKASS

--------------------------------
##Known Bugs##
