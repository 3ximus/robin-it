#! /bin/bash

if ! hash python2-pyuic5 2>/dev/null ; then
	echo "pyuic5 not installed in the system"; exit 1;
fi

for f in *.ui; do
	echo " - Compiling $f";
	python2-pyuic5 $f -o $(echo $f | sed 's/\.ui/\.py/');
done

if ! hash python2-pyrcc5 2>/dev/null ; then
	echo "pyrcc5 not installed in the system"; exit 1;
fi

for f in *.qrc; do
	echo " - Compiling $f";
	python2-pyrcc5 $f -o $(echo $f | sed 's/\.qrc/\.py/');
done

