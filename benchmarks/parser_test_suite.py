#! /usr/bin/python2

'''
Small script for testing diferent parser effects and speed
Created - 16.12.15
Copyright (C) 2015 - eximus
'''

import urllib2, sys, os
try: url_file = sys.argv[1]
except IndexError:
	print "Please give input file with list of urls to parse and path to modules containing th parser.\nUsage ./parser_test_suite.py <url_file> <module_path>."
	sys.exit()
try: import_path = sys.argv[2]
except IndexError: print "No import path selected make sure you are not using any function from other folder"
else:
	import_path = import_path.rsplit('/',1)
	sys.path.insert(0, import_path[0])
	module = __import__ (import_path[-1][:-3])

# Header
HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}

fd = open(url_file, 'r')
for url in fd:
	req = urllib2.Request(url, headers=HEADER)
	page = urllib2.urlopen(req)
	content = page.read() # Retrieve HTML
	print content
	#parser = url_lister.URLlister()
	#parser.feed(content) # Parse content
	#parser.close()
	#for url in parser.url: print url
	break
fd.close()
