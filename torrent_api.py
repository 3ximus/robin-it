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
KICKASS = "http://kickass.unblocked.la/"
HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Sa    fari/537.11'}
ORDER_SEEDS = "?field=seeders&sorder=desc"
ORDER_AGE = "?field=time_add&sorder=desc"

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
def build_search_url(main_url, search_term, order_results = 'seeds', verbose = True):
	if order_results == 'seeds': order_results = ORDER_SEEDS
	elif order_results == 'age': order_results = ORDER_AGE
	else: raise TypeError('\033[1;31mUnknown order_results parameter\033[0m')

	search_url = ''
	search_url = (main_url + 'usearch/' + urllib2.quote(search_term, safe='') + order_results)
	if verbose: print "\033[0;32mPage Link: \033[0m%s" % search_url
	return search_url


'''
Parse Page Links
Receives a page and uses the received parser (defaults to the URL_lister) to parse the page content.
Returns a list with the parsed content.
'''
def parse_page_links(url, parser=URL_lister()):
	request = urllib2.Request(url, headers=HEADER)
	try:
		page = urllib2.urlopen(request)
	except urllib2.URLError:
		if verbose: print "\033[1;31mName or Service Unknown:\033[0m %s" % url
	content = page.read() # Retrieve HTML
	parser.feed(content) # Parse content
	parser.close()
	page.close()
	returned_urls = parser.url
	parser.reset()
	return returned_urls

'''
Search
Searches the given url with a given parser for links to other web pages or magnets.
Returns a list with found links.
NOTE: Magnets will not be correctly interpreted by other functions.
'''
def search(url, parser=URL_lister(), allow_magnets = False, max_results_amount = 25, verbose = True):
	link_list = []
	regex = '.*\.html' + ('|magnet:?.*' if allow_magnets else '')
	match_pattern = re.compile(regex)
	if verbose: print "\033[0;32mSearching...\033[0m"
	links = parse_page_links(url, parser)

	# search links
	for link in links:
		matches = match_pattern.findall(link)
		match = [match for match in matches if match not in link_list]
		if match: link_list.extend(match)
	if verbose: print "\033[0;32mFound: \033[0m%d results on 1st page" % len(link_list)
	# fix links
	for i in range (len(link_list)): link_list[i] = KICKASS + link_list[i].split('/')[-1]
	return link_list[0:max_results_amount]


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
	matches = []
	cont = 1
	select_pattern = 'https.*torcache.*'
	match_pattern = re.compile(select_pattern)
	for host_page in host_url_list: # go through all supllied links
		if verbose: print "\033[0;32m\rFetching [%d / %d]...\033[0m" % (cont, len(host_url_list)),
		sys.stdout.flush()
		links = parse_page_links(host_page)
		for link in links: # search for link matching https://torcache
			matches = match_pattern.findall(link)
			if matches:
				link_list.extend(matches)
				break
		if not matches: # no matches found
			if verbose: print "\033[1;31mNo download links in page:\033[0m %s" % host_url
		cont = cont + 1
	# fix links
	for i in range (len(link_list)): link_list[i] = link_list[i] + '.torrent'
	if verbose: print "\n%d links fetched sucessfully." % (cont - 1)
	return link_list


'''
Parse File names
Given a string parses it to look nicer.
If url is set to True it tries to grab only the file name.
If remove useless its set to True it will try to remove useless names.
'''
def parse_name(name, url = False, remove_useless = False):
	new_name = ''
	tv_show_pattern = 's[0-9]*e[0-9]*'
	useless = 'hdtv|rartv|torrent|killers|ettv|fum|x[0-9]*|web|dl|fleet|avi'
	if url: name = name.split("]")[-1]
	for string in name.split('.'):
		if remove_useless and re.search(useless,string): continue
		new_name = new_name + ' ' + string.capitalize()
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
def download_file(url, fname, folder = './cache/', name_parser = False):
	if not os.path.exists(folder):
		os.mkdir(folder)
	if name_parser: fname = name_parser(fname)
	fname = folder + fname
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
def download_url_list(link_list, verbose = True, name_parser = False, folder = './cache/'):
	# convert to list
	if type(link_list) is not list: link_list = [link_list,]
	file_list = []
	cont = 1
	for link in link_list:
		filename = link.split("]")[-1]
		if verbose: print "\r\033[0;32mDownloading File [%d / %d]\033[0m" % (cont, len(link_list)),
		sys.stdout.flush()
		file_list.append(download_file(link, filename, folder=folder, name_parser=name_parser))
		cont = cont + 1
	return file_list


'''
Test program
'''
if __name__ == '__main__':
	try: # Input
		search_terms = sys.argv[1]
	except IndexError:
		print "No search term given"
		sys.exit()
	search_me = build_search_url(KICKASS, search_terms)
	search_results = search(search_me)
	download_links = get_download_links(search_results)
	download_url_list(download_links)
	print "\nDONE"
