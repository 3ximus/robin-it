#! /usr/bin/python2
import urllib2, url_lister, sgmllib

URL = "https://kickass.unblocked.pe/maze-runner-the-scorch-trials-2015-1080p-bluray-h264-aac-rarbg-t11617288.html" 

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
req = urllib2.Request(URL, headers=hdr)

try:
    page = urllib2.urlopen(req)
except urllib2.HTTPError, e:
    print e.fp.read()

content = page.read()
parser = url_lister.URLlister()
try:
	parser.feed(content)
except sgmllib.SGMLParseError:
	print "[ERROR] SGMLParser : "
parser.close()
for url in parser.url: print url
