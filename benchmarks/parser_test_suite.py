#! /usr/bin/python2

'''
Small script for testing diferent parser effects and speed
Usage example: ./parser_test_suite.py url_x10_kickass_usearch.txt "$(dirname $(pwd))/torrent_api.py"
Created - 16.12.15
Copyright (C) 2015 - eximus
'''



import urllib2, sys, os
try: url_file = sys.argv[1]
except IndexError:
	print "Feed me father!\nUsage ./parser_test_suite.py <url_file> <module_path>."
	sys.exit()
try: import_path = sys.argv[2]
except:
	print "Are you expecting me to guess the module, you little \033[1;31mcunt\033[0m?.\nUsage ./parser_test_suite.py <url_file> <module_path>."
	sys.exit()
else:
	import_path = import_path.rsplit('/',1)
	sys.path.insert(0, import_path[0])
	try: module = __import__ (import_path[-1][:-3])
	except:
		print "That shit is \033[1;31mNOT FUCKING REAL\033[0m!!\nUsage ./parser_test_suite.py <url_file> <module_path>."
		sys.exit()
try:
	for i, c in enumerate(sys.argv):
		if c == "-p":
			parser = sys.argv[i+1]
			break
		elif i == argc: raise # no name given raise exception
except: print "Brave you are, not giving a parser name, believe in jesus you must"
else:
	try: parser = getattr(module, parser) # assign parser the function of the module
	except AttributeError:
		print "What is this \033[1;31mshit\033[0m? %s, a parser name? I dont think so.\nUsage ./parser_test_suite.py <url_file> <module_path>." % parser
		sys.exit()

# Header
HEADER = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
fd = open(url_file, 'r')
for url in fd:
	req = urllib2.Request(url, headers=HEADER)
	page = urllib2.urlopen(req)
	content = page.read() # Retrieve HTML
	#print content
	#parser = url_lister.URLlister()
	#parser.feed(content) # Parse content
	#parser.close()
	#for url in parser.url: print url
	break
fd.close()
