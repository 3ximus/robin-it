#! /bin/bash

# default test sample amount
if [ -z "$1" ]; then
	echo "Insert number of test samples";
	return;
else
	sample=$1
fi
echo -e "[\033[1;33m*\033[0m] \033[3;29m Running $sample tests\033[0m";

date=$(date +%d-%b-%y-%T)
cpu_info=$(cat /proc/cpuinfo | grep -m1 "model name" | cut -d' ' -f5)
uname=$(uname -rm)
# use the torrent_api as module containing
parser_module="$(dirname $(pwd))/torrent_api.py"

mkdir -p "outJunk/$cpu_info\ $uname/$date"
i=$sample
t_real=0
t_user=0
t_sys=0
while [ $i -ge 1 ]
do
	read real user sys <<< $((time -p ./parser_test_suite.py url_x10_kickass_usearch.txt $parser_module > /dev/null) 2>&1 | cut -d ' ' -f2);
	t_real=$(echo "$t_real + $real"|bc);
	t_user=$(echo "$t_user + $user"|bc);
	t_sys=$(echo "$t_sys + $sys"|bc);
	i=$(( $i - 1 ));
	echo "Test runs left: $i";
done
t_real=$(echo "$t_real / $sample"|bc -l)
t_user=$(echo "$t_user / $sample"|bc -l)
t_sys=$(echo "$t_sys / $sample"|bc -l) 
echo -e "[\033[1;33m*\033[0m] \033[3;29mAverage Results \033[0m\nReal: $t_real s\nUser: $t_user s\nSys: $t_sys s";
