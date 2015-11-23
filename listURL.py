#! /usr/bin/python2

import url_lister, urllib

URL = raw_input("URL > ") 

usock = urllib.urlopen(URL)
parser = url_lister.URLlister()
content = usock.read()
print content
parser.feed(content)
usock.close()
parser.close()
for url in parser.url: print url
