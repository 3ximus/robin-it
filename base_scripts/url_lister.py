
'''
List URL's from a given html document
Created - 24.11.15
Copyright (C) 2015 - eximus
'''

from sgmllib import SGMLParser

class URLlister(SGMLParser):
	# reset overload
	def reset(self):
		SGMLParser.reset(self)
		self.url = []
	# caleld when "<a>" is found in the html
	# if this tag as and href then it is an url 
	def start_a(self, attrs):
		print attrs
		href = [v for k, v in attrs if k == "href"]
		if href:
			self.url.extend(href)
		
