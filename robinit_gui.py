


from PyQt4 import QtCore, QtGui
import sys

import gui.mainwindow

#class MainWindow(QDialog, gui.mainwindow.Ui_mainWindow):
#	def __init__(self, parent = None):
#		super(gui.mainwindow.Ui_mainWindow, self).__init__(parent)

app = QtGui.QApplication(sys.argv)
gui_module = gui.mainwindow.QtGui.QMainWindow()
uiform = gui.mainwindow.Ui_mainWindow()
uiform.setupUi(gui_module)
gui_module.show()
app.exec_()

