#! /usr/bin/env python2

'''
Graphical user Interface for RobinIt
Created - 30.12.15
Copyright (C) 2015 - eximus
'''

__version__ = '1.3'

# ------- KIVY IMPORTS ----------
from kivy.app import App
from kivy.lang import Builder # to import .kv file
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import Screen, ScreenManager, \
									SlideTransition, ScreenManagerException
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import AsyncImage
from kivy.uix.behaviors import ButtonBehavior
from kivy.event import EventDispatcher
from kivy.animation import Animation
from kivy.properties import ListProperty, \
							NumericProperty, \
							BooleanProperty, \
							ObjectProperty, \
							OptionProperty, \
							StringProperty

# ------- OTHER IMPORTS ----------
from random import randint
from math import sin
from functools import partial
import os, sys
# ------- USER API ----------
from robinit_api import UserContent
import webbrowser

# --- Some variable definitions for customization ---

# yellow / green theme colors
# this value is dinamic, meaning it can be extended to add more colors in the r,g,b format
theme_colors = [[0.2, 0.8, 0.2, 1], # green
				[0.98, 0.97, 0.08], # yellow
				[0.78, 0.9, 0.21], # yellowish green
				[0.11, 0.95, 0.55]] # greenish blue

# default font
theme_font = 'gui_style/fonts/VertigoFLF.ttf'

# --- USER STATE ----
User_State = None
USER_STATE_DIR = "user/"
USER_STATE_FILE = ''

# --- BACK LIGHTS GLOBALS ---
L_MAX_OPACITY = 0.5 # max backlights opacity
L_MIN_OPACITY = 0 # min backlights opacity
L_COLOR_CHANGE_TIME = 5 # time it takes for target color to change
L_OPACITY_RESLOPE = 4

# --- SELECTION BOX GLOBALS ---
SB_SIZE = 1 # height of selection box in decimal ratio of selected item width

P_TEXT_SIZE = 25 # poster container text size
P_POSTER_HEIGHT = 280 # poster container height

B_BANNER_HEIGHT = 60 # banner container height

# --- SLIDE MENU GLOBALS ---
SM_BUTTON_WIDTH = 100 # buttons width
SM_BUTTON_HEIGHT = 60 # buttons height
SM_TEXT_SIZE = 30 # size of text on the buttons
SM_HEIGHT = 10 # distance from bottom of the screen
SM_MOVEMENT_TIME = 0.2 # time of raise / lower animation

# ------------------------------------
#               BOXES
# ------------------------------------

class SelectionBox(Widget):
	'''Box to mark selected items'''
	pass

class MarkWatchedBox(Widget):
	'''Box to mark watched items'''
	pass

class MarkUnwatchedBox(Widget):
	'''Box to mark unwatched items'''
	pass

class MarkCompletedBox(Widget):
	'''Box to mark completed items'''
	pass

class MarkPendingBox(Widget):
	'''Box to mark pending items'''
	pass

class ThemeHighlight(Widget):
	'''Box to put behind titles'''
	pass

# ------------------------------------
#            IMAGES
# ------------------------------------

class WebImage(AsyncImage):
	pass

class ImagePoster(WebImage):
	pass

class ImageBanner(WebImage):
	pass

class EpisodeImage(WebImage):
	pass

# ------------------------------
#         BACKGROUND
# ------------------------------

class BackLight(Widget):
	_timer_c = 0
	_prev_color_time = 0
	_adjust_hf = 0 # horizontal adjustment to compensate frequency change
	image = StringProperty('') # image source
	l_color = ListProperty([1, 1, 1]) # color
	frequency = 1 # rate that opacity changes
	color_gradient = (0,1) # color gradient between 2 colors of the theme_colors list

	def __init__(self, image, color, **kwargs):
		super(BackLight, self).__init__(**kwargs)
		self.image = image
		self.l_color = color
		self.opacity = 0
		Clock.schedule_interval(self.update, 1/10) # update background, 30 fps
		Clock.schedule_interval(self.re_slope, L_OPACITY_RESLOPE) # every 4 seconds change the frequency
		self.re_slope(0) # initial re_slope for randomness

	def update(self, dt):
		'''Updates background lights'''
		self._timer_c += dt # count time
		self.color_interpolation()
		# opacity sin function -- (amplitude * sin(frequency * x + horizontal translation) + vertical translation)
		# function -- diff(max,min) * sin(frequency * compensator * x + match_frequency ) + (min + max) / 2  --> divide by 2 to keep constraint of max opacity
		self.opacity = ((L_MAX_OPACITY - L_MIN_OPACITY) * sin(self._timer_c * self.frequency + self._adjust_hf) + (L_MAX_OPACITY + L_MIN_OPACITY)) / 2

	def color_interpolation(self):
		'''Calculate current color based on elapsed time since last change and'''
		elapsed_time = self._timer_c - self._prev_color_time
		# linear interpolation (base value + % of change * (color mismatch))
		# start by calculating color change percentage based on elapsed time
		percentage = elapsed_time/L_COLOR_CHANGE_TIME
		# calculate color mismatch (RGB) multiply by percentage and add base color
		for i in range(3): # for r, g and b
			self.l_color[i] = theme_colors[self.color_gradient[0]][i] + ( \
					theme_colors[self.color_gradient[1]][i] \
					- theme_colors[self.color_gradient[0]][i]) * percentage
		# reached target color, regradient
		if percentage >= 1:
			self.re_gradient()

	def re_gradient(self):
		'''Calculate new gradient'''
		new_color = self.color_gradient[1]
		while new_color == self.color_gradient[1]: # force diferent color
			new_color = randint(0,len(theme_colors)-1)
		self.color_gradient = (self.color_gradient[1], new_color)
		self._prev_color_time = self._timer_c

	def re_slope(self, dt):
		'''Calculate a new random frequency for opacity function'''
		prev_frequency = self.frequency
		self.frequency = randint(10,20) * 0.01
		# create horizontal translation on sin function so that opacity
		# matches on both frequencies, making a seamless transition
		# formula -- c2 = (f1 - f2)x + c1
		self._adjust_hf = (prev_frequency - self.frequency) * self._timer_c + self._adjust_hf

class Background(FloatLayout):
	'''Background configuration'''
	def __init__(self, **kwargs):
		super(Background, self).__init__(**kwargs)
		self.light_bl = BackLight(image='gui_style/images/backlight_l.png',
								color=theme_colors[0])
		self.light_br = BackLight(image='gui_style/images/backlight_r.png',
								color=theme_colors[1])
		self.light_tl = BackLight(image='gui_style/images/backlight_t.png',
								color=theme_colors[2])
		self.add_widget(self.light_bl)
		self.add_widget(self.light_br)
		self.add_widget(self.light_tl)

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

class Selector:
	'''Handles item selection

	This is binded to on_selection event by default
	but can be binded to a specific method with bind_to(<method>)
	'''
	selected_list = [] # amount of selected items

	def __init__(self):
		event_manager.bind(on_selection=self.handle_selection)

	def bind_to(self, method):
		'''Binds the new function method passed to the on_selection event

		If unbind_selctor is passed it will unbind this selector and
		only bind the given funtion
		'''
		event_manager.bind(on_selection=method)

	def unbind_from(self, method):
		'''Unbinds given function from on_selection event'''
		event_manager.unbind(on_selection=method)

	def re_bind(self):
		'''Binds the selector default handler to on_selection event'''
		event_manager.bind(on_selection=self.handle_selection)

	def unbind(self):
		'''Unbinds the selector default handler from on_selection event'''
		event_manager.unbind(on_selection=self.handle_selection)

	def handle_selection(self, event_instance,
						what_was_selected, linked_content, value, *args):
		'''Adds selected item and its link to a list or removes them'''
		if value: self.selected_list.append((what_was_selected, linked_content))
		else: self.selected_list.remove((what_was_selected, linked_content))

	def get_selection(self, gui=False, linked=False):
		'''Return selected elements

		Parameters:
			gui -- to return only list of gui elements selected
			linked -- to return only a list of linked elements of selection
		If both are kept false or true the full list is returned
		'''
		if gui and not linked: return map(lambda x:x[0],self.selected_list)
		elif linked and not gui: return map(lambda x:x[1],self.selected_list)
		else: return self.selected_list

	def on_selected_list(self, instance, value):
		'''Called when self.selected_list content is changed'''
		pass

	def clear_selected(self):
		'''Clear everything from the selected list'''
		for tup in self.selected_list:
			tup[0].selected = False # triggering unselect
		self.selected_list = []

class SingleSelector(Selector):
	'''Handles single item selection'''

	def handle_selection(self, event_instance,
						what_was_selected, linked_content, value, *args):
		'''Overload function. Only allows 1 selected item at a time'''
		if value:
			self.clear_selected()
			self.selected_list.append((what_was_selected, linked_content))
		else: self.clear_selected()

# ------------------------------------
#           ITEM CONTAINERS
# ------------------------------------

class ItemContainer(ButtonBehavior, FloatLayout):
	'''General item conatiner definition -- see overloads

	Triggers on_selected events
	Must contain a link to the Content it displays
	Its usable displayed atributes are generally
		image, title and description
	Other atributes may be added in specific instances
	Check derived classes for specific attributes and variations
	The status variable can take the values described, and should be used as follows
		unwatched -- available but not watched (mainly for tv shows)
		watched -- watched until this point (mainly for tv shows)
		completed -- completed (and watched for tv shows)
		pending -- not available yet (mainly for movies)
	'''
	selected = BooleanProperty(False)
	linked_content = ObjectProperty(None)
	status_box = None
	status = OptionProperty("pending", options=["watched",
												"unwatched",
												"completed",
												"pending"])

	def __init__(self, linked_content, **kwargs):
		super(ItemContainer, self).__init__(**kwargs)
		self.linked_content = linked_content
		self.selection_box = SelectionBox(size_hint=(None, None))

	def on_press(self):
		'''Image is pressed behavior'''
		if self.selected:
			self.selected = False # triggers deselect effect
		else:
			self.selected = True # triggers select effect

	def on_release(self):
		'''Image is released behavior'''
		if not self.selected: # reversed due to self.selected being done on on_press
			# launch on_selected event
			event_manager.select(self, self.linked_content, False)
		else:
			# launch on_selected event
			event_manager.select(self, self.linked_content, True)

	def update_status(self):
		'''Action to force status to be updated based on linked_content'''
		pass

	def on_status(self, instance, value):
		'''Action to take when self.status changes'''
		if value == "watched": self._set_status_box(MarkWatchedBox)
		elif value == "unwatched": self._set_status_box(MarkUnwatchedBox)
		elif value == "completed": self._set_status_box(MarkCompletedBox)
		elif value == "pending": self._set_status_box(MarkPendingBox)
		else: raise ValueError("Wrong State on ItemContainer")

	def _set_status_box(self, box_type):
		'''Sets status box to a given box class and displays it

		Must not be called directly
		Allways change the value of status to automaticly trigger this function
		'''
		if self.status_box: self.remove_widget(self.status_box)
		self.status_box = box_type(size_hint=(None, None))
		self.add_widget(self.status_box)

	def on_size(self, *args):
		'''Action taken on resize, will call update structure'''
		self.update_structure()

	def update_structure(self):
		'''Called on resize, must contain size and position rules for selection and status boxes'''
		self.status_box.size = self.size
		self.status_box.pos = self.pos

	def on_selected(self, instance, value):
		'''Action to take when self.selected changes'''
		if value: self.select_effect()
		else: self.unselect_effect()

	def select_effect(self):
		'''Remove status box to "make space" for the select effect'''
		if self.status_box: self.remove_widget(self.status_box)
		self.add_widget(self.selection_box)

	def unselect_effect(self):
		'''Add status box again after deselection'''
		self.remove_widget(self.selection_box)
		self.add_widget(self.status_box)

class BannerContainer(ItemContainer):
	'''General container with only the banner -- see overloads'''
	def __init__(self, **kwargs):
		super(BannerContainer, self).__init__(**kwargs)
		self.image = ImageBanner(source=self.linked_content.banner)
		self.add_widget(self.image)

	def update_structure(self, *args):
		'''Update size and position of items'''
		super(BannerContainer, self).update_structure()
		# limit status box to image banner status box
		self.status_box.size = (self.height*self.image.image_ratio, self.height*SB_SIZE)
		self.status_box.y = self.y
		self.status_box.x = self.x + (self.width-self.height*self.image.image_ratio)/2
		# update image pos with own pos
		self.image.pos = self.pos
		# limit selection box to image banner
		self.selection_box.size = (self.height*self.image.image_ratio, self.height*SB_SIZE)
		self.selection_box.y = self.y
		self.selection_box.x = self.x + (self.width-self.height*self.image.image_ratio)/2

class ShowBannerContainer(BannerContainer):
	'''Show container with only the banner'''
	def __init__(self, **kwargs):
		super(ShowBannerContainer, self).__init__(**kwargs)
		self.counter = ThemeCounter()
		self.c_highlight = CounterHightlight()
		self.add_widget(self.c_highlight)
		self.add_widget(self.counter)
		self.update_status()

	def update_status(self):
		'''Action to force status to be updated based on linked_content'''
		self.status = self.linked_content.get_status()
		total_unwatched = 0
		for ep_list in self.linked_content.get_unwatched_episodes().values():
			total_unwatched += len(ep_list)
		self.counter.text = str(total_unwatched)

	def update_structure(self, *args):
		'''Update size and position of items'''
		super(ShowBannerContainer, self).update_structure()
		self.c_highlight.y = self.y
		self.c_highlight.center_x = self.right - 15 - \
								(self.width - self.height * self.image.image_ratio)/2
		self.counter.y = self.y
		self.counter.center_x = self.right - 15 - \
								(self.width - self.height * self.image.image_ratio)/2

class PosterContainer(ItemContainer):
	'''General container with only the poster -- see overload'''
	def __init__(self, **kwargs):
		super(PosterContainer, self).__init__(**kwargs)
		self.image = ImagePoster(source=self.linked_content.poster)
		self.add_widget(self.image)

	def update_structure(self, *args):
		'''Update size and position of items'''
		super(PosterContainer, self).update_structure()
		# limit status box to image banner status box
		self.status_box.size = (self.height*self.image.image_ratio, self.height*SB_SIZE)
		self.status_box.y = self.y
		self.status_box.x = self.x + (self.width-self.height*self.image.image_ratio)/2
		# update image pos with own pos
		self.image.pos = self.pos
		# limit selection box to image banner
		self.selection_box.size = (self.height*self.image.image_ratio, self.height*SB_SIZE)
		self.selection_box.y = self.y
		self.selection_box.x = self.x + (self.width-self.height*self.image.image_ratio)/2

class ShowPosterContainer(PosterContainer):
	'''Show Container with poster and description'''

	def __init__(self, **kwargs):
		super(ShowPosterContainer, self).__init__(**kwargs)
		self.update_status() # will also generate new labels
		self.add_widget(self.title_highlight)
		self.add_widget(self.title)
		self.add_widget(self.unwatched_count)
		self.add_widget(self.rating)
		self.add_widget(self.imdb)

	def update_structure(self, *args):
		'''Update size and position of items'''
		self.status_box.size = self.size
		self.status_box.pos = self.pos
		# calculate offset and size
		image_width = self.height * self.image.image_ratio
		x_offset = (self.width - image_width)/2

		self.image.y = self.y
		self.image.x = self.x - x_offset

		self.title_highlight.pos = (self.x + image_width, self.y + P_POSTER_HEIGHT*0.8)
		self.title_highlight.width = self.width - image_width
		self.title_highlight.height = P_POSTER_HEIGHT*0.2

		self.title.pos = (self.x + image_width/2, self.y + P_POSTER_HEIGHT*0.4)
		self.unwatched_count.pos = (self.x + image_width/2, self.y + P_POSTER_HEIGHT*0.2)
		self.rating.pos = (self.x + image_width/2, self.y - P_POSTER_HEIGHT*0)
		self.imdb.pos = (self.x + image_width/2, self.y - P_POSTER_HEIGHT*0.2)

		self.selection_box.size = self.size
		self.selection_box.pos = self.pos

	def update_status(self):
		'''Action to force status to be updated based on linked_content'''
		self.status = self.linked_content.get_status()

		self.title = Label(text=self.linked_content.name,
							font_name=theme_font,
							font_size=P_TEXT_SIZE)
		self.title_highlight = ThemeHighlight()
		# count unwatched
		total_unwatched = sum([len(e) for e in self.linked_content.get_unwatched_episodes().values()])
		self.unwatched_count = Label(text='Episodes to watch: %d' % total_unwatched,
							font_name=theme_font,
							font_size=P_TEXT_SIZE)
		self.rating = Label(text='Rating: [color=ffbf00]%s[/color]' % self.linked_content.rating,
							markup=True,
							font_name=theme_font,
							font_size=P_TEXT_SIZE)
		self.imdb = Label(text='[ref=imdb][color=00bfff]IMDB[/color][/ref]',
							markup=True,
							font_name=theme_font,
							font_size=P_TEXT_SIZE)
		self.imdb.bind(on_ref_press=self.open_imdb_link)

	def open_imdb_link(self, instance, value):
		'''Open IMDB link'''
		webbrowser.open(self.linked_content.imdb_id)

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

class AllShowsGrid(ScrollableGrid):
	def handle_state_update(self, *args):
		'''Update Grid Content with all shows'''
		self.clear_widgets()
		completed = []
		watched = []
		unwatched = []
		for show in User_State.shows:
			item = ShowPosterContainer(linked_content=User_State.shows[show])
			item.size_hint_y = None
			item.height = P_POSTER_HEIGHT
			# select correct list to append to
			locals()[User_State.shows[show].get_status()].append(item)
		for item in unwatched + watched + completed:
			self.add_widget(item)

	def on_size(self, *args):
		'''Sets amount of columns when layout size is changed (resize)'''
		if self.right < 760: self.cols = 1
		elif self.right < 1160: self.cols = 2
		elif self.right < 1560: self.cols = 3
		else: self.cols = 4

class ShowsToWatchGrid(ScrollableGrid):
	def handle_state_update(self, *args):
		'''Update Grid Content with all shows'''
		self.clear_widgets()
		sorted_list = []
		for show in User_State.shows:
			item = ShowBannerContainer(linked_content=User_State.shows[show])
			item.size_hint_y = None
			item.height = B_BANNER_HEIGHT
			if User_State.shows[show].get_status() == 'unwatched':
				sorted_list.append(item)
		# sort list being the key the sum of unwached episodes
		sorted_list.sort(reverse=True, key=(lambda i: sum([len(e) for e in i.linked_content.get_unwatched_episodes().values()])))
		# add sorted list
		for a in sorted_list:
			self.add_widget(a)

	def on_size(self, *args):
		'''Sets amount of columns when layout size is changed (resize)'''
		if self.right < 670: self.cols = 1
		elif self.right < 1015: self.cols = 2
		elif self.right < 1365: self.cols = 3
		else: self.cols = 4

# ------------------------------
#       BUTTONS & POPUPS
# ------------------------------

class ThemeTitle(Label):
	pass

class ThemeCounter(Label):
	pass

class CounterHightlight(Widget):
	pass

class ThemeButton(Button):
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

class SlidingButtonsMenu(FloatLayout):
	'''Menu with buttons that slide in and out -- must be added as a widget to work'''
	button_list = ListProperty([])
	raised = False

	def __init__(self, *args, **kwargs):
		'''Class constructor

		Arguments passed will be treated as buttons to add as follows:
			SlidingButtonsMenu(button1=method1, button2=method2)
		This will generate 2 buttons, the first named button1 will call the method1 when pressed,
		same for button2
		'''
		super(SlidingButtonsMenu, self).__init__(**kwargs)
		for button in kwargs:
			# create a new self._button_<button name>
			self.__dict__.update({'_button_' + button:
					ThemeButton(text=button, font_size=SM_TEXT_SIZE,
							size_hint=(None, None), size=(SM_BUTTON_WIDTH,SM_BUTTON_HEIGHT))})
			# button_list will contain all self.buttons
			self.button_list.append(self.__dict__['_button_'+button])
			# bind button pressed/released to the passed method
			self.__dict__['_button_'+button].bind(on_release=kwargs[button])
			# finally add the button to the layout
			self.add_widget(self.__dict__['_button_'+button])

	def update_structure(self):
		'''Update position for buttons -- should be called to keep buttons updated'''
		start_x = len(self.button_list)/2 * (SM_BUTTON_WIDTH+10)
		for i, button in enumerate(self.button_list):
			button.pos=(self.center_x - start_x + i * (SM_BUTTON_WIDTH+10),
						(SM_HEIGHT if self.raised else -SM_BUTTON_HEIGHT))

	def raise_buttons(self):
		'''Animation to raise buttons'''
		anim = Animation(y=SM_HEIGHT, duration=SM_MOVEMENT_TIME, transition='in_cubic')
		for button in self.button_list:
			Animation.cancel_all(button)
			button.opacity = 1
			anim.start(button)
		self.raised = True

	def lower_buttons(self):
		'''Animation to lower buttons'''
		anim = Animation(y=-SM_BUTTON_HEIGHT, duration=SM_MOVEMENT_TIME, transition='out_cubic')
		# action to take after the buttons left the screen
		anim.bind(on_complete=self._after_lowering_buttons)
		for button in self.button_list:
			Animation.cancel_all(button)
			anim.start(button)
		self.raised = False

	def _after_lowering_buttons(self, *args):
		for button in self.button_list:
			button.opacity = 0

# ------------------------------
#            SCREENS
# ------------------------------

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

class ShowsMainScreen(Screen):
	pass

class AllShowsScreen(Screen):
	'''Screen containing a view of all shows'''
	def on_pre_enter(self):
		''' Executed before entering '''
		# catch selection events and handle by opening new screen with show view
		# TODO Handle this with the selector
		event_manager.bind(on_selection=self.handle_selection)
		# if a view screen was open, remove it
		try: self.manager.remove_widget(self.manager.get_screen('view_show'))
		except ScreenManagerException: pass

	def handle_selection(self, event_instance,
						what_was_selected, linked_content, value, *args):
		'''Triggered when a on_selection event ocurrs'''
		if value:
			what_was_selected.selected = False # unselect
			self.new_screen(linked_content)
		else: # not likely this will be triggered
			pass

	def on_pre_leave(self):
		''' Executed before leaving '''
		event_manager.unbind(on_selection=self.handle_selection)

	def new_screen(self, show):
		'''Create new view show screen with'''
		screen = ShowViewScreen(name='view_show', linked_content=show, prev_screen=self.name)
		self.manager.add_widget(screen)
		self.manager.transition.direction = 'up'
		self.manager.current = 'view_show'

class ShowViewScreen(Screen):
	linked_content = ObjectProperty(None)
	prev_screen = StringProperty('')

	def __init__(self, linked_content, prev_screen, **kwargs):
		super(ShowViewScreen, self).__init__(**kwargs)
		self.linked_content = linked_content
		self.prev_screeen = prev_screen
		self.show_title = ThemeTitle(text=self.linked_content.name)
		self.add_widget(self.show_title)

	def on_size(self, *args):
		'''Called on each resize'''
		self.show_title.pos = (self.center_x, self.top - 90)

	def on_enter(self):
		'''Called when entering'''
		self.show_title.pos = (self.center_x, self.top - 90)

class EpisodeViewScreen(Screen):
	linked_content = ObjectProperty(None)
	prev_screen = StringProperty('')

	def __init__(self, linked_content, prev_screen, **kwargs):
		super(EpisodeViewScreen, self).__init__(**kwargs)
		self.linked_content = linked_content
		self.prev_screeen = prev_screen
		self.show_title = ThemeTitle(text=self.linked_content.name)
		self.add_widget(self.show_title)

	def on_size(self, *args):
		'''Called on each resize'''
		self.show_title.pos = (self.center_x, self.top - 90)

	def on_enter(self):
		'''Called when entering'''
		self.show_title.pos = (self.center_x, self.top - 90)

class ToWatchScreen(Screen):
	'''Screen with shows to watch'''
	def __init__(self, **kwargs):
		super(ToWatchScreen, self).__init__(**kwargs)
		self.selector = SingleSelector()
		# create a slidding menu with Watched button and View button
		self.button_menu = SlidingButtonsMenu(Watched=self.toogle_watched_action,
												View=self.view_action)
		self.add_widget(self.button_menu)

	def option_menu(self, event_instance, what_was_selected, linked_content, value):
		'''Display option menu'''
		if value: self.button_menu.raise_buttons()
		else: self.button_menu.lower_buttons()

	def view_action(self, *args):
		'''Action to take on "View" button release'''
		# since is a single selector we can get only the first element
		self.new_screen(self.selector.get_selection(linked=True)[0])

	def new_screen(self, show):
		'''Create new view show screen with'''
		screen = EpisodeViewScreen(name='ep_view_show',
									linked_content=show, prev_screen=self.name)
		self.manager.add_widget(screen)
		self.manager.transition.direction = 'left'
		self.manager.current = 'ep_view_show'

	def toogle_watched_action(self, *args):
		'''Action to take on "Watched" button release'''
		self.selector.get_selection(linked=True)[0].toogle_watched()
		self.selector.clear_selected()
		self.button_menu.lower_buttons()
		event_manager.update_gui()

	def on_size(self, *args):
		'''Called on resize'''
		self.button_menu.update_structure()

	def on_enter(self, *args):
		'''Called when entering'''
		self.button_menu.update_structure()

	def on_pre_enter(self):
		'''Called before entering screen'''
		self.selector.bind_to(self.option_menu)
		# if a view screen was open, remove it
		try: self.manager.remove_widget(self.manager.get_screen('ep_view_show'))
		except ScreenManagerException: pass

	def on_pre_leave(self):
		'''Called before leaving screen'''
		self.button_menu.lower_buttons()
		self.selector.unbind_from(self.option_menu)
		self.selector.clear_selected()

class MoviesMainScreen(Screen):
	pass

class InfoContainer(FloatLayout):
	'''Version and author information'''
	pass

class LoadingMessageContainer(FloatLayout):
	'''Loading Status information'''
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
screen_manager.add_widget(ShowsMainScreen(name = 'shows_main_screen'))
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
root.add_widget(LoadingMessageContainer())

class RobinItApp(App):
	''' APP CLASS '''
	def build(self):
		return root

if __name__ == '__main__':
	RobinItApp().run()

