#! /bin/sh
if [ -d "cache" ]; then
	rm -r cache
fi
if [ -d "user" ]; then
	rm -r user
fi
echo Done
