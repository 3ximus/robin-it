#! /usr/bin/python2

''' 
Frontend application for torrent searching and download for Kickass 
Created - 24.11.15
Copyright (C) 2015 - eximus
'''

import urllib2, urllib, sys, re
from sgmllib import SGMLParser

KICKASS = "http://kickass.unblocked.la/"
HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Sa    fari/537.11'}
ORDER_SEEDS = "?field=seeders&sorder=desc"

class URL_lister(SGMLParser):
	# overload reset on SGMLParser
	def reset(self):
		SGMLParser.reset(self)
		self.url= [] 
	def start_a(self, attrs):
		self.url.extend([y for (x,y) in attrs if x == 'href'])
	def start_td(self, attrs):
		pass						

def build_url(main_url, search_term, order_results):
	search_url = ''
	search_url = (main_url + 'usearch/' + urllib2.quote(search_terms, safe='') + order_results)
	print "\033[0;32mPage Link: \033[0m%s" % search_url
	return search_url
	
def parse_page_links(url, parser=URL_lister()):
	request = urllib2.Request(url, headers=HEADER)
	page = urllib2.urlopen(request)
	content = page.read() # Retrieve HTML
	parser.feed(content) # Parse content
	parser.close()
	return parser.url
	
def search(url, parser=URL_lister(), allow_magnets = False):
	link_list = []
	regex = '.*\.html' + ('|magnet:?.*' if allow_magnets else '')
	match_pattern = re.compile(regex)
	print "\033[0;32mSearching...\033[0m"
	links = parse_page_links(url, parser)
	
	# search links
	for link in links:
		matches = match_pattern.findall(link)
		match = [match for match in matches if match not in link_list]
		if match: link_list.extend(match)
	print "\033[0;32mFound: \033[0m%d results on 1st page" % len(link_list)
	# fix links
	for i in range (len(link_list)): link_list[i] = KICKASS + link_list[i].split('/')[-1]
	return link_list

def download_torrents(host_url_list):
	link_list = []
	links = []
	select_pattern = 'https.*torcache.*'
	substitute_pattern = '.torrent?title='
	match_pattern = re.compile(select_pattern)
	sub_pattern = re.compile(substitute_pattern)
	for host_page in host_url_list:
		links = parse_page_links(host_page)
		for link in links:
			matches = match_pattern.findall(link)
			for match in matches:
				temp = [match,]
				re.sub(substitute_pattern, '/', temp[0])
				link_list.extend(temp)
				break		
	# fix links
	for i in range (len(link_list)): link_list[i] = link_list[i] + '.torrent'
	#for link in link_list: print link
	return link_list
	

if __name__ == '__main__':
	try: # Input
		search_terms = sys.argv[1]
	except IndexError:
		print "No URL given"
		sys.exit()
	search_me = build_url(KICKASS, search_terms, ORDER_SEEDS)
	search_results = search(search_me, allow_magnets=False)
	download_torrents(search_results)
