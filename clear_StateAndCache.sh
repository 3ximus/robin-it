#! /bin/sh
if [ -d "cache" ]; then
	rm -r cache
fi
if [ -d "user" ]; then
	rm -r user

if [ -d "storage" ]; then
	rm -r storage
fi
echo Done
