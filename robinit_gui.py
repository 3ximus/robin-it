#! /usr/bin/env python2

'''
Graphical user Interface for RobinIt
Created - 30.12.15
Copyright (C) 2015 - eximus
'''

from kivy.app import App
from kivy.lang import Builder # to import .kv file
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.bubble import Bubble
from kivy.uix.image import AsyncImage
from kivy.uix.behaviors import ButtonBehavior
from kivy.event import EventDispatcher
from kivy.animation import Animation
from kivy.properties import ListProperty, NumericProperty, BooleanProperty
from random import random, randint
from functools import partial

# yellow / green theme colors
theme_colors = [[0.98, 0.97, 0.08], # yellow
				[0.78, 0.9, 0.21], # yellowish green
				[0.11, 0.95, 0.55], # greenish blue
				[0.2, 0.8, 0.2, 0.5]] # green

# --- BACKGROUND BOKEH GLOBALS ---
B_SPAWNED = 2 # set number of bokehs spawned each time
B_SPAWN_TIME_INTERVAL = 1 # time interval between each spawn
B_MAX_OPACITY = 0.3 # maximum opacity a bokeh can reach
B_OPACITY_RATE = 0.04 # rate of opacity change, less == more screen time
B_MIN_SIZE = 20 # minimum bookeh size
B_MAX_SIZE = 150 # maximum bokeh size

# --- SELECTION BAR GLOBALS ---
S_BAR_SIZE = 80
S_MOVEMENT_TIME = 0.2

# ------------------------------
#         BACKGROUND
# ------------------------------

class BokehLight(Widget):
	_timer_c = 0

	# Set default values
	velocity = ListProperty([0.1, 0.1]) # bokeh velocity
	r_color = ListProperty([1, 1, 1]) # bokeh color
	r_width = NumericProperty(100) # bokeh width
	r_height = NumericProperty(100) # bokeh size
	max_opacity = NumericProperty(1) # maximum opacity a particle can reach
	_opacity = NumericProperty(0.01) # starting opacity
	slope = B_OPACITY_RATE # rate that opacity changes
	slope_invert = False # limit the inversion of the slope to happen only once

	def __init__(self, **kwargs):
		super(BokehLight, self).__init__(**kwargs)
		Clock.schedule_interval(self.update, 1/60) # 60 times per sec

	def update(self, dt):
		self._timer_c += dt
		# update position
		self.x += self.velocity[0]
		self.y += self.velocity[1]
		# opacity control
		if self._opacity >= self.max_opacity and not self.slope_invert:
			self.slope = 0 - self.slope # invert slope
			self.slope_invert = True # make invert only happen once
		# calculate new opacity
		self._opacity += self._timer_c * self.slope * 0.001

''' Background containing moving bokeh lights spawned and moving randomly '''
class Background(FloatLayout):
	def __init__(self, **kwargs):
		super(Background, self).__init__(**kwargs)
# spawn bokeh lights in defined intervals
# use a callback function with partial to set amount of spawned bokeh per clock time
		Clock.schedule_interval(partial(self.chain_spawn, B_SPAWNED), B_SPAWN_TIME_INTERVAL)
		Clock.schedule_interval(self.remove_hidden, 0.3) # 3.33 times per sec

	def remove_hidden(self, dt):
		# remove decayed bokehs
		for bok in self.children:
			if bok._opacity <= 0:
				self.remove_widget(bok)

	'''Spawn multiple'''
	def chain_spawn(self, n, *largs):
		for i in range(n):
			self.spawn()

	''' Spawns a bokeh light '''
	def spawn(self):
		new_bokeh = BokehLight()
		# spawning position
		new_bokeh.center_y = -10 # little bellow the screen
		new_bokeh.center_x = self.center_x + randint(-10,10) * self.center_x/10
		# since they spawn on the bottom, make them go up and to the sides
		new_bokeh.velocity[0] = randint(-10, 10) * 0.02
		new_bokeh.velocity[1] = 0.1 + random() * 0.2
		new_bokeh.r_color = theme_colors[randint(0, len(theme_colors) -1 )]
		new_bokeh.max_opacity = B_MAX_OPACITY - random() * 0.2 # max value opacity cna reach
		size_val = randint(B_MIN_SIZE, B_MAX_SIZE)
		# set size
		new_bokeh.r_width = size_val
		new_bokeh.r_height = size_val
		self.add_widget(new_bokeh) # actually spawn the bockeh


# ------------------------------------
#               EVENTS
# ------------------------------------
class MultiEventDispatcher(EventDispatcher):
	def __init__(self, **kwargs):
		self.register_event_type('on_selection')
		super(MultiEventDispatcher, self).__init__(**kwargs)

	'''
	Function called on the event dispatcher to trigger a on_selection event
	Params  should be a s follows:
		what_was_selected: instance of gui selection
		linked_content: instance of content that the gui "points" to
		value: True if seleced, False if unselected
	'''
	def select(self, what_is_selected, linked_content , value):
		self.dispatch('on_selection', what_is_selected, linked_content, value)

	''' Default handler for the on_selection event '''
	def on_selection(self, what_is_selected, linked_content, value, *args):
		pass

	# GENERATE EVENT DISPATCHERS

event_manager = MultiEventDispatcher()

# ------------------------------------
#             SHOWS GRID
# ------------------------------------

class ImagePoster(ButtonBehavior, AsyncImage):
	pass

class Placeholder:
	pass

class ImageBanner(ButtonBehavior, AsyncImage):
	selected = BooleanProperty(False)
	linked_content = Placeholder()

	''' When Image is pressed '''
	def on_press(self):
		if self.selected > 0:
			self.selected = False
			event_manager.select(self, self.linked_content, False) # launch selected event
		else:
			self.selected = True
			event_manager.select(self, self.linked_content, True) # launch selected event

	'''
	Catch self.selected change event
	Params:
		instance: represents self
		value: selection value, True if selected, False if unselected
	'''
	def on_selected(self, instance, value):
# TODO instead of colouring use rectangle in the canves BUT DONT FUCKING FORGET TO PUT
# pos: self.pos , OTHERWISE IT **FUCKING** WONT MOVE!!!
		if value: self.select_effect()
		else: self.unselect_effect()

	''' Apply effect of selected '''
	def select_effect(self):
		self.color = [0.5, 0.5, 0.5, 1]

	''' Apply effect of selected '''
	def unselect_effect(self):
		self.color = [1, 1, 1, 1]


class ShowsGrid(GridLayout):
	def __init__(self, **kwargs):
		super(ShowsGrid, self).__init__(**kwargs)
		# Make sure the height is such that there is something to scroll.
		self.bind(minimum_height=self.setter('height'))
		# generate grid content
		for i in range(17):
			img = ImageBanner(
				source='http://thetvdb.com/banners/graphical/262407-g11.jpg')
			self.add_widget(img)

	''' Sets amount of columns when layout size is changed (resize) '''
	def on_size(self, *largs):
		if self.right < 650: self.cols = 1
		elif self.right < 980: self.cols = 2
		else: self.cols = 3

''' Contains show information '''
class ItemScroller(ScrollView):
	pass

# ------------------------------
#            SELECTOR
# ------------------------------

class SelectionMenuBar(Widget):
	def __init__(self, **kwargs):
		super(SelectionMenuBar, self).__init__(**kwargs)

class ShowSelectionMenuBar(SelectionMenuBar):
	def __init__(self, **kwargs):
		super(ShowSelectionMenuBar, self).__init__(**kwargs)
		butt1 = RemoveShow()
		butt2 = ToogleWatched()
		self.add_widget(butt1)
		self.add_widget(butt2)

'''
Allows item selection
Note: A selector doesn't bind itself to the on_selection event,
	due to possible conflicts events must be binded and unbinded manually
	to the handle_selection method
'''
class Selector(FloatLayout):

	selected_list = ListProperty(0) # amount of selected items
	s_raised = BooleanProperty(False) # selection menu raised

	def __init__(self, **kwargs):
		super(Selector, self).__init__(**kwargs)
		# add a hidden selection menu
		self.select_menu_bar = ShowSelectionMenuBar(pos=(0, -S_BAR_SIZE), size_hint_y=None, height=S_BAR_SIZE)
		self.add_widget(self.select_menu_bar)

	'''
	Triggered when a on_selection event ocurrs
	Params:
		event_instance: instance of MultiEventDispatcher
		what_was_selected: instance of what was selected in the gui
		linked_content: instance of linked content to gui element
		value: selection value, True if selected, False if unselected
		*args: should be empty
	'''
	def handle_selection(self, event_instance, what_was_selected, linked_content, value, *args):
		if value: self.selected_list.append((what_was_selected, linked_content))
		else: self.selected_list.remove((what_was_selected, linked_content))

	'''
	Called when self.selected_list content is changed
	Sets self.s_raised in so that a menu is raised / lowered
	Params:
		instance: represents self
		value: list with new content
	'''
	def on_selected_list(self, instance, value):
		if len(value) == 0: self.s_raised = False
		elif not self.s_raised: self.s_raised = True

	'''
	Called when self.s_raised value is changed
	Used to raise/lower selection menu
	Params:
		instance: represents self
		value: new value
	'''
	def on_s_raised(self, instance, value):
		print "haalo"
		if value == True: self.raise_selection_menu()
		else: self.lower_selection_menu()

	''' Raises the selection menu '''
	def raise_selection_menu(self):
		Animation.cancel_all(self.select_menu_bar)
		anim = Animation(x=0, y=0, duration=S_MOVEMENT_TIME)
		anim.start(self.select_menu_bar)

	''' Raises the selection menu '''
	def lower_selection_menu(self):
		Animation.cancel_all(self.select_menu_bar)
		anim = Animation(x=0, y=-S_BAR_SIZE, duration=S_MOVEMENT_TIME)
		anim.start(self.select_menu_bar)

	''' Clear everything selected selections '''
	def clear_selected(self):
		for tup in self.selected_list:
			tup[0].selected = False
		self.selected_list = []

class SingleSelector(Selector):
	'''
	Triggered when a on_selection event ocurrs
	This overloads the correspondent super function
	Params:
		event_instance: instance of MultiEventDispatcher
		what_was_selected: instance of what was selected in the gui
		linked_content: instance of linked content to gui element
		value: selection value, True if selected, False if unselected
		*args: should be empty
	'''
	def handle_selection(self, event_instance, what_was_selected, linked_content, value, *args):
		if value:
			self.clear_selected()
			self.selected_list.append((what_was_selected, linked_content))
		else: self.clear_selected()

# ------------------------------
#            BUTTONS
# ------------------------------

class ThemeButton(Button):
	pass

class RemoveShow(ThemeButton):
	pass

class ToogleWatched(ThemeButton):
	pass

# ------------------------------
#            SCREENS
# ------------------------------

class ShowsMainScreen(Screen):
	def __init__(self, **kwargs):
		super(ShowsMainScreen, self).__init__(**kwargs)

	def on_pre_enter(self):
		self.selector = Selector()
		# on_selection event on the event_manager will trigger a handle_selection
		event_manager.bind(on_selection=self.selector.handle_selection)
		self.add_widget(self.selector)
	def on_pre_leave(self):
		event_manager.unbind(on_selection=self.selector.handle_selection)

class AllShowsScreen(Screen):
	def __init__(self, **kwargs):
		super(AllShowsScreen, self).__init__(**kwargs)

	def on_pre_enter(self):
		self.selector = SingleSelector()
		# on_selection event on the event_manager will trigger a handle_selection
		event_manager.bind(on_selection=self.selector.handle_selection)
		self.add_widget(self.selector)

	def on_pre_leave(self):
		event_manager.unbind(on_selection=self.selector.handle_selection)

class MoviesMainScreen(Screen):
	pass

class MainScreen(Screen):
	pass

''' Version and author information '''
class InfoContainer(FloatLayout):
	pass

# ---------------------------------------------
#             LOAD .kv FILE
Builder.load_file('gui_style/robinit.kv')
# ---------------------------------------------

# ------------------------------------
#     SCREEN BEHAVIOR / SETTIGNS
# ------------------------------------

# EMPTY

# ------------------------------------
#           SCREEN MANAGER
# ------------------------------------
screen_manager = ScreenManager(transition=SlideTransition())
screen_manager.add_widget(MainScreen(name = 'main_screen'))
screen_manager.add_widget(ShowsMainScreen(name = 'shows_main_screen'))
screen_manager.add_widget(AllShowsScreen(name = 'all_shows_screen'))
screen_manager.add_widget(MoviesMainScreen(name = 'movies_main_screen'))

# ------------------------------------
#          THE ROOT WIDGET
# ------------------------------------
root = FloatLayout()
root.add_widget(Background())
root.add_widget(screen_manager)
root.add_widget(InfoContainer())

''' APP CLASS '''
class RobinItApp(App):
	def build(self):
		return root

if __name__ == '__main__':
	RobinItApp().run()

