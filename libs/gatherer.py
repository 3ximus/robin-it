#! /usr/bin/env python

'''
Module containing methods to search and download torrents / get magnet links
Latest Update - v1.1
Created - 24.11.15
Copyright (C) 2015 - eximus
'''

# Imports
import sys, re, os
import parserlib
import utillib

# Defines
HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}

KICKASS = "http://kickass.unblocked.la/"
TRUSTED_SOURCES = 'killers|rartv|immerse|publichd|rarbg|'
TRUSTED_SOURCES += TRUSTED_SOURCES.upper()
TRUSTED_FORMAT = 'web-dl|hdtv|eztv|ettv|'
TRUSTED_FORMAT += TRUSTED_FORMAT.upper()
ERROR_MSG = "[\033[1;31mERROR\033[0m]"

def parse_page_links(html_page, parser=parserlib.Torrent_BS4):
	'''Parse Page Links

	Mandatory attributes and methods for received parser are: 'feed(self, content)', 'close(self)' and 'parsed'
	Optional method 'reset()' is also called if available
	The feed method should return the content or store it in a class attribute named 'parsed'
	'''
	if not parser: raise ValueError("No parser specified")
	parsed = parser.feed(html_page, parse_for = 'torrent', host = KICKASS) #  choose feed parameters to get expected results from parser
	parser.close()
	if not parsed: parsed = parser.parsed # get content through parsed class atribute
	try: parser.reset() # some parsers need this workaround
	except NameError: pass
	return parsed # return list of Torrent instances

def search(main_url, search_term, parser=parserlib.Torrent_BS4(), page = 1, order_results = 'seeds'):
	'''Searches the given search_term with a given parser for links to other web pages or magnets.

	Parameters:
		main_url -- url to use on search
		search_term -- term to search for
		parser -- parser of html document
		page -- page number of search results
		order_results -- order of results, values are : 'seeds' and 'age'
	'''
	url = utillib.build_search_url(main_url, search_term, page=page, order_results=order_results)
	try: html = utillib.get_page_html(url)
	except utillib.UtillibError: raise # re-raise the exception
	return parse_page_links(html, parser) # return list of Torrent instances

def present_results(torrent_list, header=True, output=True):
	'''Receives a list with Torrent instances and outputs it in presentable form

	Parameters:
		torrent_list -- list with torrent instances
		header -- include header in return results
		output -- print results to stdout
	'''
	bold = False
	results=[]
	if header: results.append(' #. Rat | Name \t\t\t\t\t\t\t| Size\t\t| Age\t\t| Seeds\t| Peers |')
	for i, torrent in enumerate(torrent_list):
		# TODO tor class feature not working
		if re.search(TRUSTED_SOURCES, torrent.name): tor_class =  '\033[0m[\033[0;32mV\033[0m]'
		elif re.search(TRUSTED_FORMAT, torrent.name): tor_class = '\033[0m[\033[0;33m-\033[0m]'
		else: tor_class = '  '
		torrent_string = '%s%s%s %50s\t %10s\t %10s\t %s\t %s\t%s' % (
				'\033[34m' if bold else '', tor_class , '\033[34m' if bold else '',
				torrent.name[:50], torrent.size, torrent.age, torrent.seeds, torrent.peers,
				'\033[0m' if bold else '')
		results.append(torrent_string)
		bold = not bold # toogle
	if output:
		for r in results: print r
	return results

def download_torrents(torrent_list, location = './storage/'):
	'''Downloads all torrents passed as a list of Torrent instances

	Parameters:
		torrent_list -- list of torrents to download
		location -- location to save the torrents
	Note: this function yields 3 values (State of donwnload torrent (True - downloading / false - finished), instance of downloaded torrent and download status)
	'''
	if type(torrent_list) is not list: torrent_list = [torrent_list,] # convert to list
	status = True
	for torrent in torrent_list:
		yield False, torrent, status
		if not torrent: status = False
		else:
			link = "https:%s.torrent" % torrent.tor_file
			utillib.download_file(link, torrent.name, location=location, extension = '.torrent')
			status = True
		yield True, torrent, status

def get_magnets(torrent_list):
	'''Get magnet links from a Torrent list

	Returns list with magnet links
	'''
	magnets = []
	for torrent in torrent_list:
		magnets.append(torrent.magnet)
	return magnets

