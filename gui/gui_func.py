
'''
Set of generic GUI functions
Latest Update - v0.3
Created - 30.1.16
Copyright (C) 2016 - eximus
'''

__version__ = '0.3'


from PyQt5 import QtCore

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
