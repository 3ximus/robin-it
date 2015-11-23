#! /bin/sh
echo $(./listURL2.py | egrep "https.*torcache" | sed 's/.torrent?title=/\//')".torrent"
