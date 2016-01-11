#! /usr/bin/env sh
echo "Installing prerequisites..."
pip install -r requirements.txt
apt-get install python-pygame python-lxml
