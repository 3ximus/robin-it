#!/usr/bin/python2

import urllib
sock = urllib.urlopen("http://google.com/")
htmlread = sock.read()
sock.close()
print htmlread
