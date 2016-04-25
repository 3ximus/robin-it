'''
Library Containing various utility functions
Containts Exception class UtillibError
Latest Update - v1.1
Created - 28.12.15
Copyright (C) 2015 - eximus
'''

import urllib2, urllib, requests
import re, os, sys


HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
ERROR_MSG = "[\033[1;31mERROR\033[0m]"

class UtillibError(Exception):
	'''Custom Error class'''
	pass

def build_search_url(main_url, search_term, page = 1, order_results = 'seeds'):
	'''Build URL based on search arguments and other parameters

	Parameters:
		main_url -- main page to build urls from
		search_term -- term to search for on that page
		order_results -- order results, accepted values are 'seeds' and 'age'
	Note: building search url uses a keyword 'usearch' wich may not work in most websites ( works for KICKASS )
	'''

	ORDER_SEEDS = "?field=seeders&sorder=desc"
	ORDER_AGE = "?field=time_add&sorder=desc"

	if order_results == 'seeds': order_results = ORDER_SEEDS
	elif order_results == 'age': order_results = ORDER_AGE
	else: raise TypeError('%s Unknown order_resutls parameter' % ERROR_MSG)
	search_url = '%susearch/%s/%d/%s' % (main_url, urllib2.quote(search_term, safe=''), page, order_results)
	return search_url

def get_page_html(url):
	'''Get html index of given page'''
	request = urllib2.Request(url, headers=HEADER) # make a request for the html
	try: page = urllib2.urlopen(request) # open the html file
	except urllib2.URLError: raise UtillibError("%s Name or service Unknown: %s" % (ERROR_MSG, url))
	content = page.read() # Return HTML
	page.close() # close the retrieved html
	return content

def parse_name(name, url = False, remove_useless = False, tv_show = False, split_char = '.', capitalize = False, force_show = None, ignore = None):
	'''Parse names into some desired format

	Parameters:
		name -- name to be parsed
		url -- if True it tries to grab only the filename contained in it
		tv_show -- if True it tries to look for patterns like s01e02
		split_char -- char present in the string separating the various names
		capitalize -- strings to capitalize
		remove_useless -- if True tries to remove useless names
		force_show -- regex pattern force existance, overrides ignore strings
		ignore -- regex pattern to ignore, ignored if string is existent in force_show
	'''
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


def download_file(url, fname, location = './cache/', name_parser = False, extension = ''):
	'''Download file at the given url

	Parameters:
		url -- url holding the file
		fname -- name given to the download file
		location -- location to save the file. Defaults to ./cache/
		name_parser -- function to parse filenames
		extension -- extension given to the file
	'''
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



