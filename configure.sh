#! /bin/bash


# verify if pyuic5 is installed
if hash python2-pyuic5 2>/dev/null ; then
	pyuic=python2-pyuic5
elif hash pyuic5 2>/dev/null; then
	pyuic=pyuic5
else
	echo "pyuic5 not installed in the system"; exit 1;
fi

# compile .ui files
for f in gui/resources/ui/*.ui; do
	echo " - Compiling $f";
	$pyuic $f -o $(echo $f | sed 's/\/ui\/\(.*\)\.ui/\/\1\.py/');
done

# verify if pyrcc5 is installed
if hash python2-pyrcc5 2>/dev/null ; then
	pyrcc=python2-pyrcc5
elif hash pyrcc5 2>/dev/null ; then
	pyrcc=pyrcc5
else
	echo "pyrcc5 not installed in the system"; exit 1;
fi

# compile .qrc files
for f in gui/resources/*.qrc; do
	echo " - Compiling $f";
	$pyrcc $f -o $(echo $f | sed 's/\.qrc/_rc\.py/');
done

echo "Done"
