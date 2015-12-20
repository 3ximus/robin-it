#! /usr/bin/python2

'''
Small script for testing diferent parser effects and speed
v1.0.0
Usage example: ./parser_test_suite.py url_x10_kickass_usearch.txt "$(dirname $(pwd))/torrent_api.py" URL_lister
Created - 16.12.15
Copyright (C) 2015 - eximus
'''

import urllib2, sys, os

try: # get arguments
	url_file = sys.argv[1]
	import_path = sys.argv[2]
	parser = sys.argv[3]
	log_output = sys.argv[4]
except IndexError: sys.exit("[ERROR] Missing arguments\nUsage ./parser_test_suite.py <url_file> <module_path> <parser_name>.\nExample: ./parser_test_suite.py url_x10_kickass_usearch.txt $(dirname $(pwd))/torrent_api.py URL_lister log.txt")
else:
	import_path = import_path.rsplit('/',1) # strip path and select the path to import directory
	sys.path.insert(0, import_path[0]) # add path to system path variable
	try: # try importing modules and getting function by name
		module = __import__ (import_path[-1][:-3])
		parser = getattr(module, parser) # assign parser the function of the module
	except (AttributeError, ImportError, ValueError): sys.exit("[ERROR] Unexistent module or parser function")

# Header to make requests
HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
fd = open(url_file, 'r')
log_fd = open(log_output, 'w+')
for url in fd:
	req = urllib2.Request(url, headers=HEADER)
	page = urllib2.urlopen(req)
	content = page.read() # Retrieve HTML
	try: parser_instance = parser() # create new instance of parser classobj
	except TypeError: sys.exit("[ERROR] Given parser is not an instanceable object")
	try: parser_instance.feed(content) # call feed method with the html to be parsed
	except NameError: sys.exit("[ERROR] Given parser does not contain feed() method")
	parser_instance.close() # close parser object is called
	for chewed in parser_instance.parsed: log_fd.write(chewed) # retrived parsed content stored in the parsed variable attribute of the parser class
fd.close()
log_fd.close()
