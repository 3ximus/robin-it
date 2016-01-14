#! /usr/bin/env python2

'''
Graphical user Interface for RobinIt
Created - 30.12.15
Copyright (C) 2015 - eximus
'''

__version__ = '1.3'

from kivy.app import App
from kivy.lang import Builder # to import .kv file
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.carousel import Carousel
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition, ScreenManagerException
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import AsyncImage
from kivy.uix.behaviors import ButtonBehavior
from kivy.event import EventDispatcher
from kivy.animation import Animation
from kivy.properties import ListProperty, NumericProperty, BooleanProperty, ObjectProperty
from random import random, randint
from functools import partial
import os, sys
from robinit_api import UserContent

# yellow / green theme colors
theme_colors = [[0.2, 0.8, 0.2, 0.5], # green
				[0.98, 0.97, 0.08], # yellow
				[0.78, 0.9, 0.21], # yellowish green
				[0.11, 0.95, 0.55]] # greenish blue

# default font
theme_font = 'gui_style/fonts/VertigoFLF.ttf'

# --- USER STATE ----
User_State = None
USER_STATE_DIR = "user/"
USER_STATE_FILE = ''

# --- BACKGROUND BOKEH GLOBALS ---
B_SPAWNED = 2 # set number of bokehs spawned each time
B_SPAWN_TIME_INTERVAL = 1 # time interval between each spawn
B_MAX_OPACITY = 0.3 # maximum opacity a bokeh can reach
B_OPACITY_RATE = 0.04 # rate of opacity change, less == more screen time
B_MIN_SIZE = 20 # minimum bookeh size
B_MAX_SIZE = 150 # maximum bokeh size

# --- SELECTION BAR GLOBALS ---
S_BAR_SIZE = 500
S_MOVEMENT_TIME = 0.2
S_BAR_OPACITY = 0.6

class Placeholder:
	'''  PLACEHOLDER CLASS '''
	pass

# ------------------------------
#         BACKGROUND
# ------------------------------

class Background(FloatLayout):
	'''Background configuration'''
	pass

# ------------------------------------
#               EVENTS
# ------------------------------------
class MultiEventDispatcher(EventDispatcher):
	def __init__(self, **kwargs):
		self.register_event_type('on_selection')
		self.register_event_type('on_state_update')
		super(MultiEventDispatcher, self).__init__(**kwargs)

	def select(self, what_is_selected, linked_content , value):
		'''Function to trigger on_selection event

		Arguments:
		what_was_selected -- instance of GUI selection
		linked_content -- instance of content that the GUI "points" to
		value -- True if seleced, False if unselected
		'''
		self.dispatch('on_selection', what_is_selected, linked_content, value)

	def update_gui(self, *args):
		'''Function to trigger on_state_update event'''
		self.dispatch('on_state_update', *args)

	def on_selection(self, what_is_selected, linked_content, value, *args):
		'''Default handler for the on_selection event'''
		pass

	def on_state_update(self, *args):
		'''Default handler for the on_state_update event'''
		pass

	# GENERATE EVENT DISPATCHERS

event_manager = MultiEventDispatcher()

# ------------------------------
#            SELECTOR
# ------------------------------

class Selector(FloatLayout):
	'''Handles item selection

	This is binded to on_selection event by default
	but can be binded to a specific method with bind_to(<method>)
	'''

	selected_list = ListProperty(0) # amount of selected items
	s_raised = BooleanProperty(False) # selection menu raised

	def __init__(self, **kwargs):
		super(Selector, self).__init__(**kwargs)
		if side_bar: # add side_bar
			self.show_side_bar = ShowSideBar()
			self.add_widget(self.show_side_bar)
		self.allow_side_bar=side_bar
		event_manager.bind(on_selection=self.handle_selection)

	def handle_selection(self, event_instance,
						what_was_selected, linked_content, value, *args):
		'''Adds selected item and its link to a list or removes them'''
		if value: self.selected_list.append((what_was_selected, linked_content))
		else: self.selected_list.remove((what_was_selected, linked_content))

	def on_selected_list(self, instance, value):
		'''Called when self.selected_list content is changed'''
		if self.allow_side_bar: # if side bar is allowed
			if len(value) == 0: self.s_raised = False
			elif not self.s_raised: self.s_raised = True

	def on_s_raised(self, instance, value):
		'''Called when self.s_raised value is changed'''
		if value == True: self.raise_selection_menu()
		else: self.lower_selection_menu()

	def raise_selection_menu(self):
		'''Raises the selection menu'''
		self.show_side_bar.raise_bar()

	def lower_selection_menu(self):
		'''Raises the selection menu'''
		self.show_side_bar.lower_bar()

	def clear_selected(self):
		'''Clear everything from the selected list'''
		for tup in self.selected_list:
			tup[0].selected = False # triggering unselect
		self.selected_list = []

class SingleSelector(Selector):
	'''Handles single item selection'''

	def handle_selection(self, event_instance,
						what_was_selected, linked_content, value, *args):
		'''Overload function. Only allows 1 selected item'''
		if value:
			self.clear_selected()
			self.selected_list.append((what_was_selected, linked_content))
		else: self.clear_selected()

class SelectionMenuBar(Widget):
	pass

class ShowSideBar(SelectionMenuBar):
	def __init__(self, **kwargs):
		super(ShowSideBar, self).__init__(**kwargs)
		self.size_hint_x = None
		self.width = S_BAR_SIZE
		self.opacity = 0

	def on_size(self, *args):
		''' Called to correctly set initial position on resize '''
		self.x = self.right

	def raise_bar(self):
		''' Raise the side menu '''
		Animation.cancel_all(self)
		anim = Animation(x=root.right - S_BAR_SIZE, y=0, duration=S_MOVEMENT_TIME, transition = 'in_cubic')
		anim.bind(on_start = self.on_start)
		anim.start(self)

	def lower_bar(self):
		''' Lower the side menu '''
		Animation.cancel_all(self)
		anim = Animation(x=root.right, y=0, duration=S_MOVEMENT_TIME, transition = 'out_cubic')
		anim.bind(on_complete = self.on_complete)
		anim.start(self)

	def on_start(self, *args):
		''' Binded to the begining of the raise animation '''
		self.opacity = S_BAR_OPACITY # show bar

	def on_complete(self, *args):
		''' Binded to the completion of lower animation '''
		self.opacity = 0 # hide bar after completion

# ------------------------------------
#            BUTTON IMAGES
# ------------------------------------

class ItemContainer(ButtonBehavior, FloatLayout):
	'''General item conatiner

	Triggers on_selected events
	Contains a Title, an Image and a description
	'''
	selected = BooleanProperty(False)
	linked_content = None
	image = None

	def __init__(self, image=None, linked_content=None, title='', description='', **kwargs):
		super(ItemContainer, self).__init__(**kwargs)

	def on_release(self):
		'''Image is pressed beahvior'''
		if self.selected > 0:
			self.selected = False
			# launch on_selected event
			event_manager.select(self, self.linked_content, False)
		else:
			self.selected = True
			# launch on_selected event
			event_manager.select(self, self.linked_content, True)

	def on_selected(self, instance, value):
		'''Action to take when self.selected changes'''
		if value: self.select_effect()
		else: self.unselect_effect()

	def select_effect(self):
		'''Apply effect of select -- should be overloaded'''
		pass

	def unselect_effect(self):
		'''Apply effect of unselect --  should be overloaded'''
		pass

class ImageButton(ButtonBehavior, AsyncImage):
	selected = BooleanProperty(False)
	linked_content = Placeholder()

	def on_release(self):
		'''Image is pressed beahvior'''
		if self.selected > 0:
			self.selected = False
			# launch on_selected event
			event_manager.select(self, self.linked_content, False)
		else:
			self.selected = True
			# launch on_selected event
			event_manager.select(self, self.linked_content, True)
	def on_selected(self, instance, value):
		'''Action to take when self.selected changes'''
# TODO instead of colouring use rectangle in the canves BUT DONT FUCKING FORGET TO PUT
# pos: self.pos , OTHERWISE IT **FUCKING** WONT MOVE!!!
		if value: self.select_effect()
		else: self.unselect_effect()

	def select_effect(self):
		'''Apply effect of select'''
		self.color = [0.5, 0.5, 0.5, 1]

	def unselect_effect(self):
		'''Apply effect of unselect'''
		self.color = [1, 1, 1, 1]

class ImagePoster(ImageButton):
	pass

class ImageBanner(ImageButton):
	pass

class EpisodeImage(ImageButton):
	pass

# ------------------------------------
#             SHOWS GRID
# ------------------------------------
class ItemScroller(ScrollView):
	'''Container for scrollable Layouts'''
	pass

class ScrollableGrid(GridLayout):
	def __init__(self, **kwargs):
		super(ScrollableGrid, self).__init__(**kwargs)
		# Make sure the height is such that there is something to scroll.
		self.bind(minimum_height=self.setter('height'))
		event_manager.bind(on_state_update=self.handle_state_update)

	def handle_state_update(self, *args):
		'''Called when update GUI event is triggered'''
		pass

	def on_size(self, *largs):
		'''Sets amount of columns when layout size is changed (resize)'''
		if self.right < 650: self.cols = 1
		elif self.right < 980: self.cols = 2
		else: self.cols = 3

class AllShowsGrid(ScrollableGrid):
	def handle_state_update(self, *args):
		'''Update Grid Content with all shows'''
		self.clear_widgets()
		for show in User_State.shows:
			source = User_State.shows[show].banner
			self.add_widget(ItemContainer())
			img = ImageBanner(source= source)
			img.linked_content = User_State.shows[show]
			self.add_widget(img)


# ------------------------------
#       BUTTONS & POPUPS
# ------------------------------

class ThemeTitle(Label):
	pass

class ThemeButton(Button):
	pass

class RemoveShow(ThemeButton):
	pass

class ToogleWatched(ThemeButton):
	pass

class UsernamePopup(Popup):
	def __init__(self, **kwargs):
		'''Build The Popup'''
		super(UsernamePopup, self).__init__(**kwargs)
		layout = BoxLayout(orientation='vertical')
		self.username = TextInput(text='fabio', font_name=theme_font, font_size=30, multiline=False)
		self.butt = ThemeButton(text='Validate', font_size=30)
		layout.add_widget(self.username)
		layout.add_widget(self.butt)
		self.content=layout
		# bind actions
		self.username.bind(on_text_validate=self.load_user) # when 'enter' is pressed
		self.butt.bind(on_release=self.load_user) # when button is clicked call load_user

	def load_user(self, *args):
		''' Load user based on username input '''
		user_name = self.username.text
		if  user_name != "":
			USER_STATE_FILE = "%srobinit_%s_%s%s" % (USER_STATE_DIR, __version__, user_name, '.pkl') # Only used to look for state file
			if not os.path.exists(USER_STATE_FILE): # no previous save file?
				# TODO GENERATE NEW USER POPUP
				pass
			else:
				global User_State # refer to the global User_State to make changes
				# set global User State
				User_State = UserContent(user_name)
				User_State.load_state(USER_STATE_DIR)
				event_manager.update_gui()
				self.parent.remove_popups()

	def generate_new_user(self):
		''' Generate a new user '''
		pass

class PopupShade(FloatLayout):
	pass

# ------------------------------
#            SCREENS
# ------------------------------

class AllShowsScreen(Screen):
	def __init__(self, **kwargs):
		super(AllShowsScreen, self).__init__(**kwargs)

	''' Executed before entering '''
	def on_pre_enter(self):
		# catch selection events and handle by opening new screen with show view
		event_manager.bind(on_selection=self.handle_selection)
		# remove a view screen when returning
		try: self.manager.remove_widget(self.manager.get_screen('view_show'))
		except ScreenManagerException: pass

	'''
	Triggered when a on_selection event ocurrs
	Params:
		event_instance: instance of MultiEventDispatcher
		what_was_selected: instance of what was selected in the GUI
		linked_content: instance of linked content to GUI element
		value: selection value, True if selected, False if unselected
		*args: should be empty
	'''
	def handle_selection(self, event_instance, what_was_selected, linked_content, value, *args):
		if value:
			what_was_selected.selected = False # unselect
			self.new_screen(linked_content)
		else: # not likely this will be triggered
			pass

	''' Executed before leaving '''
	def on_pre_leave(self):
		event_manager.unbind(on_selection=self.handle_selection)

	'''
	Create new view show screen with
	'''
	def new_screen(self, show):
		screen = ShowViewScreen(name='view_show')
		screen.add_widget(ThemeTitle(text=show.name, pos=(self.center_x, self.top - 90)))
		# TODO SETUP THE NEW SCREEN WITH SHOW INFO
		self.manager.add_widget(screen)
		self.manager.transition.direction = 'up'
		self.manager.current = 'view_show'

class ShowViewScreen(Screen):
	pass

class ToWatchScreen(Screen):
	'''
	Builds the show main screen
	Structure is as follows:
		TODO
	'''
	def __init__(self, **kwargs):
		super(ToWatchScreen, self).__init__(**kwargs)

	def on_pre_enter(self):
		pass

	def on_size(self, *args):
		pass

	def on_pre_leave(self):
		pass

class MoviesMainScreen(Screen):
	pass

class MainScreen(Screen):
	def __init__(self, **kwargs):
		super(MainScreen, self).__init__(**kwargs)
		self.popup_shade = PopupShade()
		self.popup = UsernamePopup()
		self.add_widget(self.popup_shade)
		self.add_widget(self.popup)

	def on_size(self, *args):
		self.popup.center_x = self.right / 2
		self.popup.center_y = self.top / 2

	def remove_popups(self):
		self.popup.dismiss()
		self.remove_widget(self.popup)
		self.remove_widget(self.popup_shade)

class InfoContainer(FloatLayout):
	''' Version and author information '''
	pass

# ---------------------------------------------
#             LOAD .kv FILE
Builder.load_file('gui_style/robinit.kv')
Builder.load_file('gui_style/items.kv')
# ---------------------------------------------

# ------------------------------------
#           SCREEN MANAGER
# ------------------------------------
screen_manager = ScreenManager(transition=SlideTransition())
screen_manager.add_widget(MainScreen(name = 'main_screen'))
screen_manager.add_widget(ToWatchScreen(name = 'to_watch_screen'))
screen_manager.add_widget(AllShowsScreen(name = 'all_shows_screen'))
screen_manager.add_widget(MoviesMainScreen(name = 'movies_main_screen'))

# ------------------------------------
#          THE ROOT WIDGET
# ------------------------------------
root = FloatLayout()
root.add_widget(Background())
root.add_widget(screen_manager)
root.add_widget(InfoContainer())

class RobinItApp(App):
	''' APP CLASS '''
	def build(self):
		return root

if __name__ == '__main__':
	RobinItApp().run()

