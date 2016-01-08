#! /usr/bin/env python

'''
Frontend console aplication to search tv show torrents
Uses Kickass torrents
Latest Update - v1.2
Created - 11.12.15
Copyright (C) 2015 - eximus
'''

import torrents as torrent_api
from utillib import UtillibError
import sys, re

BIAS = 2
SEASON_MAX = 10
QUALITY_PRESET = '720p'
DOWNLOAD_PATH = './storage/'

try:
	tv_show = raw_input("\033[1;33mTV Show name > \033[0m")
	quality = raw_input("\033[1;33mQuality (1080p, 720p, other)> \033[0m")
	quality = (quality if quality else QUALITY_PRESET)
	seasons = raw_input("\033[1;33mSeasons > \033[0m").split(' ')
	if seasons == ['']:
		print 'Please insert correct number of seasons'
		sys.exit(-1)
	episodes = raw_input("\033[1;33mEpisodes > \033[0m").split(' ')
except KeyboardInterrupt:
	print "\033[1;31m\nExiting...\033[0m"
	sys.exit()
for s in seasons:
	if episodes == [''] and seasons != ['']:
# download all season episodes
		episodes = range(SEASON_MAX + 1)[1:] # skip 0
	for e in episodes:
		ep_id = ''
		try: ep_id = 'S%02d' % int(s) + 'E%02d' % int(e)
		except ValueError:
			print 'How hard could it possibly be? The numbers Mason!! Give me NUMBERS!!'
			sys.exit(-1)
		search_term = '%s %s %s' % (tv_show, ep_id, quality)
		print 'Searching: %s' % search_term
		try: search_results = torrent_api.search(torrent_api.KICKASS, search_term)
		except UtillibError:
			print "No results found"
			continue
		torrent_api.present_results(search_results)

		downloads = []
		choice = raw_input("\nSelection: ")
		for c in choice.split(' '):
			downloads.append(search_results[int(c)])

		files_downloaded = torrent_api.download_torrents(downloads, location=DOWNLOAD_PATH)
		print 'Files Downloaded: %d, to %s' % (len(files_downloaded), DOWNLOAD_PATH)

