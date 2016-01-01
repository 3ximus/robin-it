#! /usr/bin/env python

''' 
Search Kickass for torrents/magnets of given keyword
Created - 24.11.15
Copyright (C) 2015 - eximus
'''

import urllib2, urllib, url_lister, sys, re

try: #Input
	search_terms = sys.argv[1]
except IndexError:
	search_terms = raw_input("Search for > ")

kickass_url = "https://kickass.unblocked.la/"
# Header
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}

# Build URL
search_url = kickass_url + 'search/' +  urllib2.quote(search_terms, safe='') + '?field=seeders&sorder=desc'
print search_url
request = urllib2.Request(search_url, headers=hdr)
print "\033[0;32m%s\033[0m" % search_url
page = urllib2.urlopen(request)
content = page.read() # Retrieve HTML
parser = url_lister.URLlister()
parser.feed(content) # Parse content
parser.close()
#for url in parser.url: print url

# Start parsing links containing .html or magnet
match_pattern = re.compile('.*\.html|magnet:?.*')
for url in parser.url:
	matches = match_pattern.findall(url)
#	for match in matches: print match
