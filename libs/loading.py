'''
 Loading Displays Library
 Library for progress bar display on console
 Created - 19.9.15
 Copyright (C) 2015 - eximus
'''

def progress_bar(percent_complete, show_percentage=False, bar_body = "#", bar_empty = " ", bar_begin = "[", bar_end = "]", bar_size=20, bar_arrow=None):

	# Clamp percenteage between 0-100
	percent_complete = 0 if percent_complete < 0 else (100 if percent_complete > 100 else percent_complete)

	# Bar has a body with a maximum of 20 spaces
	dots_to_print = int(bar_size/100.0 * percent_complete)
	bar = bar_begin + bar_body * dots_to_print + (bar_arrow if bar_arrow and percent_complete != 100 else "") + bar_empty * int(bar_size - dots_to_print) + bar_end

	if not show_percentage: return bar
	else: return bar + "  %.0f %%" % percent_complete

