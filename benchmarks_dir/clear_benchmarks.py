#! /bin/sh
if [ -d "outJunk" ]; then
	rm outJunk -r;
fi
if [ -f "log.txt" ]; then
	rm log.txt -r;
fi

echo "Done"
