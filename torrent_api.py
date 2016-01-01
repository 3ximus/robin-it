#! /usr/bin/env python

'''
Module containing methods to search and download web pages or web hosted files
It can be executed using ./torrent_api <search-terms> to search and download torrents from KICKASS by default
Automaticly prints progress
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

'''
Parse Page Links
Mandatory attributes and methods for received parser are: 'feed(self, content)', 'close(self)' and 'parsed'
Optional method 'reset()' is also called if available
The feed method should return the content or store it in a class attribute named 'parsed'
'''
def parse_page_links(html_page, parser=parserlib.BS4):
	if not parser: raise ValueError("No parser specified")
	parsed = parser.feed(html_page) #  choose feed parameters to get expected results from parser
	parser.close()
	if not parsed: parsed = parser.parsed # get content through parsed class atribute
	try: parser.reset() # some parsers need this workaround
	except NameError: pass
	return parsed

'''
Search
Searches the given search_term with a given parser for links to other web pages or magnets.
Gives a Trust flag to torrents
'''
def search(main_url, search_term, parser=parserlib.BS4(), page = 1, order_results = 'seeds'):
	url = utillib.build_search_url(main_url, search_term, page=page, order_results=order_results)
	try: html = utillib.get_page_html(url)
	except utillib.UtillibError: raise # re-raise the exception
	return parse_page_links(html, parser) # get all the links from the page

'''
Receives a list with Torrent instances and outputs it in presentable form
'''
def present_results(torrent_list):
	bold = False
	print ' #. Rat | Name \t\t\t\t\t\t\t| Size\t\t| Age\t\t| Seeds\t| Peers |'
	for i, torrent in enumerate(torrent_list):
		# tor class feature not working
		if re.search(TRUSTED_SOURCES, torrent.name): tor_class =  '\033[0m[\033[0;32mV\033[0m]'
		elif re.search(TRUSTED_FORMAT, torrent.name): tor_class = '\033[0m[\033[0;33m-\033[0m]'
		else: tor_class = '  '

		print '%s%2d. %s%s %50s\t %10s\t %10s\t %s\t %s\t%s' % (
				'\033[34m' if bold else '',
				i,
				tor_class ,
				'\033[34m' if bold else '',
				torrent.name[:50],
				torrent.size,
				torrent.age,
				torrent.seeds,
				torrent.peers,
				'\033[0m' if bold else '')
		bold = not bold # toogle

'''
Download URL List
Downloads all files hosted on the given URL's
'''
def download_torrents(torrent_list, name_parser = False, location = './storage/'):
	if type(torrent_list) is not list: torrent_list = [torrent_list,] # convert to list
	file_list = []
	for torrent in torrent_list:
		link = "https:%s.torrent" % torrent.tor_file
		filename = utillib.download_file(link, torrent.name, location=location, extension = '.torrent')
		file_list.append(filename) # add the new downloaded filename to the file list
	return file_list

'''
Get magnet links from a Torrent list
'''
def get_magnets(torrent_list):
	magnets = []
	for torrent in torrent_list:
		magnets.append(torrent.magnet)
	return magnets

'''
Test program
'''
if __name__ == '__main__':
	try: search_terms = sys.argv[1]
	except IndexError: sys.exit("No search term given")
	try: results = search(KICKASS, search_terms)
	except utillib.UtillibError: sys.exit("No results found")
	present_results(results)
	try: choice = eval(raw_input("\nSelection: "))
	except (NameError, SyntaxError): sys.exit("%s Use a number" % ERROR_MSG)
	try: downloads = download_torrents(results[choice])
	except IndexError: sys.exit("%s Unexistent Option" % ERROR_MSG)
	for d in downloads:
		print "Downloaded: %s" % d
	print "\nDONE"

