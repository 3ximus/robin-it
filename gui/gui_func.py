
'''
Set of generic GUI functions
Latest Update - v0.6
Created - 30.1.16
Copyright (C) 2016 - eximus
'''

__version__ = '0.6'


from PyQt5 import QtCore
from hashlib import md5
import os
import urllib

def download_object(url, cache_dir=None, cache_this=True):
	'''Download object at the given url

		Cache directory is used to cache objects to bypass downloads
		The cache_this parameter is used to avoid writing the object to the cache
	'''
	data = None
	cache_image = False
	if cache_dir:
		cache = cache_dir+"/image/"
		if not os.path.exists(cache): os.makedirs(cache)
		md5_hash = md5()
		md5_hash.update(url)
		digest = md5_hash.hexdigest()
		if digest in os.listdir(cache):
			with open(cache+digest, "r") as image_file:
				return image_file.read()
		elif cache_this: cache_image = True
	# else... download
	try: data = urllib.urlopen(url).read()
	except IOError: print "Error Loading show banner url: %s" % url
	if cache_image and data:
		with open(cache+digest, "w") as image_file:
			image_file.write(data)
	return data

def clickable(widget):
	'''Makes a widget clickable, returning the clicked event'''
	class Filter(QtCore.QObject):
		clicked = QtCore.pyqtSignal()

		def eventFilter(self, obj, event):
			if obj == widget:
				if event.type() == QtCore.QEvent.MouseButtonRelease:
					if obj.rect().contains(event.pos()):
						# use .emit(obj) to get the object within the slot.
						self.clicked.emit()
					return True
			return False

	filter = Filter(widget)
	widget.installEventFilter(filter)
	return filter.clicked

def begin_hover(widget):
	'''Makes a widget emit a signal when mouse enters its bounds'''
	class Filter(QtCore.QObject):
		begin_hover = QtCore.pyqtSignal()

		def eventFilter(self, obj, event):
			if obj == widget:
				if event.type() == QtCore.QEvent.HoverEnter:
					self.begin_hover.emit()
					return True
			return False
	filter = Filter(widget)
	widget.installEventFilter(filter)
	return filter.begin_hover

def end_hover(widget):
	'''Makes a widget emit a signal when mouse leaves its bounds'''
	class Filter(QtCore.QObject):
		end_hover = QtCore.pyqtSignal()

		def eventFilter(self, obj, event):
			if obj == widget:
				if event.type() == QtCore.QEvent.HoverLeave:
					self.end_hover.emit()
					return True
			return False
	filter = Filter(widget)
	widget.installEventFilter(filter)
	return filter.end_hover