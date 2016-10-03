#! /bin/bash

# verify if pyuic5 is installed
if ! hash python2-pyuic5 2>/dev/null ; then
	echo "pyuic5 not installed in the system"; exit 1;
fi

# compile .ui files
for f in gui/resources/ui/*.ui; do
	echo " - Compiling $f";
	python2-pyuic5 $f -o $(echo $f | sed 's/\/ui\/\(.*\)\.ui/\/\1\.py/');
done

# verify if pyrcc5 is installed
if ! hash python2-pyrcc5 2>/dev/null ; then
	echo "pyrcc5 not installed in the system"; exit 1;
fi

# compile .qrc files
for f in gui/resources/*.qrc; do
	echo " - Compiling $f";
	python2-pyrcc5 $f -o $(echo $f | sed 's/\.qrc/_rc\.py/');
done

