#! /usr/bin/python2

'''
Frontend apllication to automatically download torrents
Created - 02.12.15
Copyright (C) 2015 - eximus
'''
import torrent_api
import sys

KICKASS = "http://kickass.unblocked.la/"
ORDER_SEEDS = "?field=seeders&sorder=desc"
ORDER_AGE = "?field=time_add&sorder=desc"

try:
	search_terms = sys.argv[1]
except IndexError:
	search_terms = raw_input("\033[1;33mSearch > \033[0m")

search_me = torrent_api.build_url(KICKASS, search_terms, ORDER_SEEDS)
search_results = torrent_api.search(search_me, allow_magnets=False, max_results_amount = 1)
#download_links = torrent_api.get_download_links(search_results)
#torrent_api.download_url_list(download_links)
print "\nDONE"
