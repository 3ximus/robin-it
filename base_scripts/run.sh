#! /bin/sh
echo -e "	\e[0;32mRetrieving for urls.txt...\e[0m"
for url in $(cat urls.txt)
do
	echo $(./list_url.py $url| egrep "https.*torcache" | sed 's/.torrent?title=/\//')".torrent"
done
