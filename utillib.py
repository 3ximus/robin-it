#! /usr/bin/python2

'''
Library Containing various utility functions
Created - 28.12.15
Copyright (C) 2015 - eximus
'''

import urllib2, urllib, requests
import re, os, sys


HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
ERROR_MSG = "[\033[1;31mERROR\033[0m]"

''' Custom Error class '''
class UtillibError(Exception):
	pass

'''
Build Search URL
Receives a string and the page URL to do the search and builds the search url for that page.
Receives the order in wich you want the results to be returned, accepted values are 'seeds' and 'age'.
NOTE: Currently only works for KICKASS Torrents page.
'''
def build_search_url(main_url, search_term, page = 1, order_results = 'seeds'):

	ORDER_SEEDS = "?field=seeders&sorder=desc"
	ORDER_AGE = "?field=time_add&sorder=desc"

	if order_results == 'seeds': order_results = ORDER_SEEDS
	elif order_results == 'age': order_results = ORDER_AGE
	else: raise TypeError('%s Unknown order_resutls parameter' % ERROR_MSG)
	search_url = '%susearch/%s/%d/%s' % (main_url, urllib2.quote(search_term, safe=''), page, order_results)
	return search_url

'''
Get Page HTML
Returns the html index given a source url
'''
def get_page_html(url):
	request = urllib2.Request(url, headers=HEADER) # make a request for the html
	try: page = urllib2.urlopen(request) # open the html file
	except urllib2.URLError: raise UtillibError("%s Name or service Unknown: %s" % (ERROR_MSG, url))
	content = page.read() # Return HTML
	page.close() # close the retrieved html
	return content

'''
Parse names
Given a string parses it to look nicer.
If url is set to True it tries to grab only the file name.
If remove useless its set to True it will try to remove useless names.
The ignore string is a regex patern to ignore
The force_show string is a regex pattern to not ignore and make uppercase
'''
def parse_name(name, url = False, remove_useless = False, tv_show = False, split_char = '.', capitalize = False, force_show = None, ignore = None):
	new_name = ''
# known patterns
	tv_show_pattern = 's[0-9]*e[0-9]*'
	useless = '^torrent$|^fum$|^x[0-9]*$|^fleet$|^BluRay$|^avi$|^mkv$|^XviD|^LD$|^WEB-DL$|^-$|HDTV'
	if url and split_char == '.':
		name = name.split("/")[-1].split("]")[-1]
		split_char = '-'
		useless += '|.*html'
	for string in name.split(split_char): # build name depending on the various values supplied
		if force_show and re.search(force_show, string): new_name += ' ' + string.upper()
		elif remove_useless and re.search(useless,string): continue
		elif ignore and re.search(ignore, string): continue
		elif tv_show and re.search(tv_show_pattern, string): new_name += ' ' + string.upper()
		else: new_name += ' ' + (string.capitalize() if capitalize else string)
	return new_name[1:]


'''
Download File
Download a file from a given URL holding the file.
By default it saves the file in './cache' by another path can be specified.
'''
def download_file(url, fname, location = './cache/', name_parser = False, extension = ''):
	if not os.path.exists(location): os.mkdir(location) # check for folder existence
	if name_parser: fname = name_parser(fname) # use a name parser to generate a better filename
	fname = '%s%s%s' % (location, fname, extension) # complete the filename with the full path
	try:
		r = requests.get(url, stream=True, headers=HEADER) # open connection to remote file
		with open(fname, 'wb') as f: # open new file
			for chunk in r.iter_content(chunk_size=1024): # download chuncks of content from the website
				if chunk:
					f.write(chunk) # write to new file
					f.flush() # flush content
	except requests.exceptions.RequestException as e:
		print '\n' + str(e)
		sys.exit(1)
	return fname



