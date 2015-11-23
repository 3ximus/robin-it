
''' List URL's from a given html document'''

from sgmllib import SGMLParser

class URLlister(SGMLParser):
	def reset(self):
		SGMLParser.reset(self)
		self.url = []
	# overrride the start_a method in SGML parser that is caleld when "<a>" is found in the html
	# if this tag as and href then it is an url 
	def start_a(self, attrs):
		href = [v for k, v in attrs if k == "href"]
		if href:
			self.url.extend(href)
		
