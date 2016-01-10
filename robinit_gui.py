#! /usr/bin/env python2

'''
Graphical user Interface for RobinIt
Created - 30.12.15
Copyright (C) 2015 - eximus
'''

import sys

from kivy.app import App
from kivy.lang import Builder # to import .kv file
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Line
from kivy.properties import ListProperty
from kivy.clock import Clock
from random import random

class BokehLight(Widget):
	velocity = ListProperty([0.1, 0.1])

	def __init__(self, **kwargs):
		super(BokehLight, self).__init__(**kwargs)
		Clock.schedule_interval(self.update, 1/60)

	def update(self, *args):
		self.x += self.velocity[0]
		self.y += self.velocity[1]

class Background(Widget):
	pass

class ShowsMainScreen(Screen):
	pass

class MoviesMainScreen(Screen):
	pass

class MainScreen(Screen):
	pass


# ---------------------------------------------
#             LOAD .kv FILE
Builder.load_file('gui_style/robinit.kv')
# ---------------------------------------------

# create the screen manager
screen_manager = ScreenManager()
screen_manager.add_widget(MainScreen(name = 'main_screen'))
screen_manager.add_widget(ShowsMainScreen(name = 'shows_main_screen'))
screen_manager.add_widget(MoviesMainScreen(name = 'movies_main_screen'))

class RobinItApp(App):
	#kv_directory = 'gui_style'
	def build(self):
# set root widget to be the screen manager
		return screen_manager

if __name__ == '__main__':
	RobinItApp().run()

