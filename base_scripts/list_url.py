#! /usr/bin/python2

''' 
Small script for listing href's in a given URL
Uses url_lister to parse html with "href" fields
Created - 24.11.15
Copyright (C) 2015 - eximus
'''

import urllib2, url_lister, sys

try: # Input
	URL = sys.argv[1]
except IndexError:
	print "No URL given"
	sys.exit()

# Header
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}

req = urllib2.Request(URL, headers=hdr)
page = urllib2.urlopen(req)
content = page.read() # Retrieve HTML
parser = url_lister.URLlister()
parser.feed(content) # Parse content
parser.close()
for url in parser.url: print url
