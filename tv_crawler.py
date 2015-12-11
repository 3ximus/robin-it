#! /usr/bin/python2

'''
Frontend apllication to search and download tv shows
Created - 11.12.15
Copyright (C) 2015 - eximus
'''
import torrent_api
import sys, re

BIAS = 10
TRUSTED_SOURCES = 'Killers|Rartv|Immerse'
TRUSTED_SOURCES = TRUSTED_SOURCES + TRUSTED_SOURCES.upper()
TRUSTED_FORMAT = 'Web|Dl|Hdtv|Eztv|Ettv'
TRUSTED_FORMAT = TRUSTED_FORMAT + TRUSTED_FORMAT.upper()

tv_show_name = raw_input("\033[1;33mTV Show name > \033[0m")

# TODO Search tv show repository

#seasons = raw_input("\033[1;33mSeasons > \033[0m")
#episodes = raw_input("\033[1;33mEpisodes > \033[0m")

# Search and disply results
search_results = torrent_api.search(torrent_api.KICKASS, tv_show_name,  max_results_amount = BIAS)
for i, result in enumerate(search_results):
	name = torrent_api.parse_name(result, url=True, remove_useless=True, tv_show = True)
	print '%2d.' % i, 
	if re.search(TRUSTED_SOURCES, name): print '[\033[0;32mV\033[0m]\t', name
	elif re.search(TRUSTED_FORMAT, name): print '[\033[1;33m-\033[0m]\t', name
	else: print '[?]\t', name
selection = raw_input('\033[1;33mSelect > \033[0m')
selection = selection.split(' ')
# Download
selected_links = []
for i in selection:
	try: selected_links.append(search_results[int(i)])
	except ValueError:
		print 'Type numbers you dumb fuck!!'
		sys.exit(-1)
download_links = torrent_api.get_download_links(selected_links)
torrent_api.download_url_list(download_links)

