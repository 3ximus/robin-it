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

# Defines
HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Sa    fari/537.11'}
KICKASS = "http://kickass.unblocked.la/"
ORDER_SEEDS = "?field=seeders&sorder=desc"
ORDER_AGE = "?field=time_add&sorder=desc"
RESULTS_PER_PAGE = 25

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
		self.url= []
	def start_a(self, attrs):
		self.url.extend([y for (x,y) in attrs if x == 'href'])
	def start_td(self, attrs):
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
	else: raise TypeError('\033[1;31mUnknown order_results parameter\033[0m')
	search_url = '%susearch/%s/%d/%s' % (main_url, urllib2.quote(search_term, safe=''), page, order_results)
	return search_url


'''
Parse Page Links
Receives a page and uses the received parser (defaults to the URL_lister) to parse the page content.
Returns a list with the parsed content.
'''
def parse_page_links(url, parser=URL_lister()):
	request = urllib2.Request(url, headers=HEADER)
	try: page = urllib2.urlopen(request)
	except urllib2.URLError:
		print "\033[1;31mName or Service Unknown:\033[0m %s" % url
		return
	content = page.read() # Retrieve HTML
	parser.feed(content) # Parse content
	parser.close()
	page.close()
	returned_urls = parser.url
	parser.reset()
	return returned_urls

'''
Search
Searches the given search_term with a given parser for links to other web pages or magnets.
Returns a list with found links.
NOTE: Magnets will not be correctly interpreted by other functions.
'''
def search(main_url, search_term, parser=URL_lister(), use_magnets = False, max_results_amount = RESULTS_PER_PAGE, verbose = True, order_results = 'seeds'):
	link_list = []
	regex = '.*\.html' + ('|magnet:?.*' if use_magnets else '')
	max_count = 0
	current_page = 0
	if verbose: print "\033[0;32mSearching...\033[0m"
	while 1:
		added = False
		current_page += 1
		url = build_search_url(main_url, search_term, page=current_page, order_results=order_results, verbose=verbose)
		links = parse_page_links(url, parser)
# search links
		if not links: break
		for link in links:
			if re.search(regex, link) and link not in link_list:
				added = True
				link_list.append(main_url + link.split('/')[-1])
				max_count += 1
			if max_count >= max_results_amount: break # loop control
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
# convert to list if has a single element
	if type(host_url_list) is not list: host_url_list = [host_url_list,]
	link_list = []
	links = []
	select_pattern = 'https.*torcache.*'
	for cont, host_page in enumerate(host_url_list): # go through all supllied links
		if verbose: print "\033[0;32m\rFetching [%d / %d]...\033[0m" % (cont + 1, len(host_url_list)),
		sys.stdout.flush()
		links = parse_page_links(host_page)
		match = False
		for link in links:
# search for link matching https://torcache
			if re.search(select_pattern, link):
				link_list.append(link)
				match = True
				break
# no matches found
		if verbose and not match: print "\033[1;31mNo download links in page:\033[0m %s" % host_url
# fix links
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
	tv_show_pattern = 's[0-9]*e[0-9]*'
	useless = '^torrent$|^fum$|^x[0-9]*|^fleet$|^avi$'
	if url and split_char == '.':
		name = name.split("/")[-1].split("]")[-1]
		split_char = '-'
		useless += '|.*html'
	for string in name.split(split_char):
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
	if not os.path.exists(location): os.mkdir(location)
	if name_parser: fname = name_parser(fname)
	fname = location + fname
	try:
		r = requests.get(url, stream=True, headers=HEADER)
		with open(fname, 'wb') as f:
			for chunk in r.iter_content(chunk_size=1024):
				if chunk:
					f.write(chunk)
					f.flush()
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
# convert to list
	if type(link_list) is not list: link_list = [link_list,]
	file_list = []
	for cont, link in enumerate(link_list):
		filename = link.split("]")[-1]
		if verbose: print "\r\033[0;32mDownloading File [%d / %d]\033[0m" % (cont + 1, len(link_list)),
		sys.stdout.flush()
		file_list.append(download_file(link, filename, location=location, name_parser=name_parser))
	if verbose: print "\r%d files downloaded sucessfully." % (cont + 1)
	return file_list


'''
Test program
'''
if __name__ == '__main__':
	try: search_terms = sys.argv[1]
	except IndexError:
		print "No search term given"
		sys.exit()
	search_me = build_search_url(KICKASS, search_terms)
	search_results = search(search_me)
	download_links = get_download_links(search_results)
	download_url_list(download_links)
	print "\nDONE"
