
'''
Set of generic GUI functions
Latest Update - v0.6
Created - 30.1.16
Copyright (C) 2016 - eximus
'''

__version__ = '0.6'


from PyQt5 import QtCore

import urllib

def download_object(url, cache_dir=None):
	'''Download object at the given url, cache directory is used to cache objects to bypass downloads'''
	data = None
	try: data = urllib.urlopen(url).read()
	except IOError: print "Error Loading show banner url: %s" % url
	return data

def clickable(widget):
	'''Makes a widget clickable, returning the clicked event'''
	class Filter(QtCore.QObject):
		clicked = QtCore.pyqtSignal()

		def eventFilter(self, obj, event):
			if obj == widget:
				if event.type() == QtCore.QEvent.MouseButtonRelease:
					if obj.rect().contains(event.pos()):
						self.clicked.emit()
						# use .emit(obj) to get the object within the slot.
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