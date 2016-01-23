if [ -z "$1" ]; then
	echo "Starting in Window Mode..."
	./robinit_gui.py --size=1100x600  # Run in window size
elif [ "$1" == "-f" ]; then
	./robinit_gui.py --auto-fullscreen # Run as fullscreen
elif [ "$1" == "-b" ]; then
	./robinit_gui.py --size=1100x600 --fake-fullscreen # Run in window size borderless
fi

