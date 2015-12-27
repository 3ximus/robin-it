#! /usr/bin/python2

'''
Module containing methods to search and download web pages or web hosted files
It can be executed using ./torrent_api <search-terms> to search and download torrents from KICKASS by default
Automaticly prints progress
Created - 24.11.15
Copyright (C) 2015 - eximus
'''

# Imports
import urllib2, urllib, sys, re, requests, os
from sgmllib import SGMLParser
from bf4 import BeautifulSoup

# Defines
HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}

KICKASS = "http://kickass.unblocked.la/"
ORDER_SEEDS = "?field=seeders&sorder=desc"
ORDER_AGE = "?field=time_add&sorder=desc"
RESULTS_PER_PAGE = 25

# Internal
ERROR_MSG = "[\033[1;31mERROR\033[0m]"

'''
URL Parser Class
Derives from the SGMLParser.
Once a html page is feeded it parses it and uses one of the rules to return its content.
The start_a parses for links on the web page.
The start_td parses for title content. Not implemented.
'''
class URL_lister(SGMLParser):
# overload reset on SGMLParser
	def reset(self):
		SGMLParser.reset(self)
		self.parsed= []
	def start_a(self, attrs):
		self.parsed.extend([y for (x,y) in attrs if x == 'href'])
	def start_td(self, attrs):
		pass

'''
Torrent data structure
'''
class Torrent():
	def __init(self):
		self.name = ""
		self.magnet = ""
		self.link = ""
		self.host = KICKASS
		self.seeds = 0
		self.peers = 0
		self.size = 0

'''
Beautiful Soup 4
Parser for BeautifulSoup 4
Returns a tuple with Torrent class
'''
class BF4():
	def __init__(self):
		pass
	def feed(self, content):
		pass
	def close(self):
		pass


'''
Build Search URL
Receives a string and the page URL to do the search and builds the search url for that page.
Receives the order in wich you want the results to be returned, accepted values are 'seeds' and 'age'.
NOTE: Currently only works for KICKASS Torrents page.
'''
def build_search_url(main_url, search_term, page = 1, order_results = 'seeds', verbose = True):
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
	except urllib2.URLError: sys.exit( "%s Name or service Unknown: %s" % (ERROR_MSG, url))
	content = page.read() # Return HTML
	page.close() # close the retrieved html
	return content

'''
Parse Page Links v1
Deprecated
Receives a page and uses the received parser (defaults to the URL_lister) to parse the page content.
Returns a list with the parsed content.
'''
def parse_page_links(url, parser=URL_lister()):
	content = get_page_html(url) # get html page
	parser.feed(content) # Parse content
	parser.close() # close parser TODO needed for url lister
	returned_urls = parser.parsed # get all the parsed content
	parser.reset() # parser must reset to avoid maintaining its value after sucessive calls
	return returned_urls

'''
Parse Page Links v2
Improve on the heavily parser dependant v1 ang give more abstraction
Mandatory attributes for received parser are: 'feed(self, content)', 'close(self)' and 'parsed'
The feed method should return the content or store it in a class attribute named 'parsed'
'''
def parse_page_links_2(html_page, parser=None):
	if not parser: return
	parsed = parser.feed(html_page) # TODO choose feed parameters to get expected results from parser
	parser.close()
	if not parsed: parsed = parser.parsed
	try: parser.reset() # some parsers need this workaround
	except NameError: pass
	return parsed

'''
Search
Searches the given search_term with a given parser for links to other web pages or magnets.
Returns a list with found links.
NOTE: Magnets will not be correctly interpreted by other functions.
'''
def search(main_url, search_term, parser=URL_lister(), use_magnets = False, max_results_amount = RESULTS_PER_PAGE, verbose = True, order_results = 'seeds'):
	link_list = []
	regex = '.*\.html' + ('|magnet:?.*' if use_magnets else '') # what to search for
	max_count = 0
	current_page = 0
	if verbose: print "\033[0;32mSearching...\033[0m"
	while 1:
		added = False # initialize loop control variable
		current_page += 1 # iterate page results
		url = build_search_url(main_url, search_term, page=current_page, order_results=order_results, verbose=verbose)
		links = parse_page_links(url, parser) # get all the links from the page
# search links
		if not links: break
		for link in links:
			if re.search(regex, link) and link not in link_list: # find all links matching the pattern
				added = True # loop control, mark found result
				link_list.append(main_url + link.split('/')[-1]) # add result to list
				max_count += 1 # count results found
			if max_count >= max_results_amount: break # inner loop control
		if added == False: break # loop control
	if verbose: print "\033[0;32mFound: \033[0m%d results on %d pages" % (max_count, current_page)
	return link_list


'''
Get Download Links
Get Download Links from a Page or multiple pages.
Returns a list with download links found.
NOTE: Only works for torrents.
'''
def get_download_links(host_url_list, verbose = True):
# convert to list if only a single url is given
	if type(host_url_list) is not list: host_url_list = [host_url_list,]
	link_list = []
	links = []
	select_pattern = 'https.*torcache.*' # pattern to look for, TODO this only works for torrents
	for cont, host_page in enumerate(host_url_list): # go through all supllied links
		if verbose: print "\033[0;32m\rFetching [%d / %d]...\033[0m" % (cont + 1, len(host_url_list)),
		sys.stdout.flush()
		links = parse_page_links(host_page) # find hiperlinks on this page
		match = False # set break condition
		for link in links: # go through all links to find one matching the pattern
			if re.search(select_pattern, link):
				link_list.append(link)
				match = True
				break # only one needed, break when found
# no matches found
		if verbose and not match: print "%s No download links in page: %s" % (ERROR_MSG, host_url)
# fix links to be in the file format
	for i in range (len(link_list)): link_list[i] += '.torrent'
	if verbose: print "\r%d links fetched sucessfully." % (cont + 1)
	return link_list


'''
Parse names
Given a string parses it to look nicer.
If url is set to True it tries to grab only the file name.
If remove useless its set to True it will try to remove useless names.
The ignore string is a regex patern to ignore
The force_show string is a regex pattern to not ignore and make uppercase
'''
def parse_name(name, url = False, remove_useless = False, tv_show = False, split_char = '.', capitalize = True, force_show = None, ignore = None):
	new_name = ''
# known patterns
	tv_show_pattern = 's[0-9]*e[0-9]*'
	useless = '^torrent$|^fum$|^x[0-9]*|^fleet$|^avi$'
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
Frontend to call parse_name with remove useless set to true
'''
def parse_name_remove_useless(name, url = False):
	return parse_name(name, url = url, remove_useless = True)


'''
Download File
Download a file from a given URL holding the file.
By default it saves the file in './cache' by another path can be specified.
'''
def download_file(url, fname, location = './cache/', name_parser = False):
	if not os.path.exists(location): os.mkdir(location) # check for folder existence
	if name_parser: fname = name_parser(fname) # use a name parser to generate a better filename
	fname = location + fname # complete the filename with the full path
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


'''
Download URL List
Downloads all files hosted on the given URL's
NOTE: Website adress formating bound, may not work everywere
'''
def download_url_list(link_list, verbose = True, name_parser = False, location = './cache/'):
	if type(link_list) is not list: link_list = [link_list,] # convert to list
	file_list = []
	for cont, link in enumerate(link_list):
		filename = link.split("]")[-1] # filename contains only the last part of the name after the ']' char
		if verbose: print "\r\033[0;32mDownloading File [%d / %d]\033[0m" % (cont + 1, len(link_list)),
		sys.stdout.flush() # flush stdout due to carriage return usage
		filename = download_file(link, filename, location=location, name_parser=name_parser) # download the file
		file_list.append(filename) # add the new downloaded filename to the file list
	if verbose: print "\r%d files downloaded sucessfully." % (cont + 1)
	return file_list


'''
Test program
'''
if __name__ == '__main__':
	try: search_terms = sys.argv[1]
	except IndexError: sys.exit("No search term given")
	search_me = build_search_url(KICKASS, search_terms)
	search_results = search(search_me)
	download_links = get_download_links(search_results)
	download_url_list(download_links)
	print "\nDONE"
