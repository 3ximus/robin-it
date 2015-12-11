#! /usr/bin/python2

'''
Frontend apllication to search and download tv shows
Created - 11.12.15
Copyright (C) 2015 - eximus
'''
import torrent_api
import sys

KICKASS = "http://kickass.unblocked.la/"

show_name = raw_input("\033[1;33mTV Show name > \033[0m")

# TODO Search tv show repository

seasons = raw_input("\033[1;33mSeasons > \033[0m")
episodes = raw_input("\033[1;33mEpisodes > \033[0m")

search_me = torrent_api.build_search_url(KICKASS, show_name, order_results='seeds')
search_results = torrent_api.search(search_me, allow_magnets=False, max_results_amount = 10)
download_links = torrent_api.get_download_links(search_results)
torrent_api.download_url_list(download_links, name_parser=torrent_api.parse_name_remove_useless)
print "\nDONE"

