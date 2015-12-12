#! /usr/bin/python2

'''
Frontend apllication to search and download tv shows
Created - 11.12.15
Copyright (C) 2015 - eximus
'''
import torrent_api
import sys, re

BIAS = 2
TRUSTED_SOURCES = 'killers|rartv|immerse|publichd'
TRUSTED_SOURCES = TRUSTED_SOURCES + TRUSTED_SOURCES.upper()
TRUSTED_FORMAT = 'web|dl|hdtv|eztv|ettv'
TRUSTED_FORMAT = TRUSTED_FORMAT + TRUSTED_FORMAT.upper()
SEASON_MAX = 10
QUALITY_PRESET = '720p'
DOWNLOAD_PATH = './cache/'

'''
List available options, generate decision making prompt to user and try to choose best match
'''
def decision(search_results, print_results = True):
	trusted_count = 0
	temp_buffer = []
	return_me = None
	if not search_results: return
	for i, result in enumerate(search_results):
		name = torrent_api.parse_name(result, url=True, remove_useless=True, tv_show = True, capitalize = False)
		temp_buffer.append('%2d.' % i)
		if re.search(TRUSTED_SOURCES, name):
			trusted_count = trusted_count + 1
			temp_buffer.append('[\033[0;32mV\033[0m]\t  %s\n' % name)
		elif re.search(TRUSTED_FORMAT, name): temp_buffer.append('[\033[1;33m-\033[0m]\t  %s\n' % name)
		else: temp_buffer.append('[?]\t  %s\n' % name)
# good distribution, select first link
	if trusted_count < 3: return search_results[1]
	print ''.join(temp_buffer)[:-1]
	selection = raw_input('\033[1;33mSelect > \033[0m')
	selection = selection.split(' ')
	selected_links = []
	for i in selection:
		try: selected_links.append(search_results[int(i)])
		except ValueError:
			print 'Type numbers you dumb fuck!! NUMBERS!!!'
			sys.exit(-1)
	return selected_links
# end decision

# ========== MAIN =========

tv_show = raw_input("\033[1;33mTV Show name > \033[0m")

# TODO Search tv show repository for availbale ep/sn

quality = raw_input("\033[1;33mQuality > \033[0m")
quality = (quality if quality else QUALITY_PRESET)
seasons = raw_input("\033[1;33mSeasons > \033[0m").split(' ')
if seasons == ['']:
	print 'What fucking season am I suposed to look for uh?? Season 0??'
	sys.exit(-1)
episodes = raw_input("\033[1;33mEpisodes > \033[0m").split(' ')
cont = 0
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
		print '\033[0;33mSearching: \033[0m%s' % search_term
# Search and disply results
		search_results = torrent_api.search(torrent_api.KICKASS, search_term, max_results_amount = BIAS, verbose = False)
		selected_links = decision(search_results, print_results = False)
		if not selected_links: continue
		if type(selected_links) is not list: print '\033[1;32mDownloading: \033[0m%s' % torrent_api.parse_name(selected_links, url=True, remove_useless=True, tv_show = True, capitalize = True, force_show = TRUSTED_SOURCES + TRUSTED_FORMAT)
# Download
		download_links = torrent_api.get_download_links(selected_links, verbose = False)
		files_downloaded = torrent_api.download_url_list(download_links, location=DOWNLOAD_PATH, verbose = False)
		cont = cont + len(files_downloaded)
print 'Files Downloaded: %d, to %s' % (cont, DOWNLOAD_PATH)
