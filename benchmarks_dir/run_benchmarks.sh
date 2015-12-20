#! /bin/bash

# Script to run and log the output of the parser_test_suite.py
# Use this instead of the python script if you want to run large amounts of tests
#Created - 16.12.15
#Copyright (C) 2015 - eximus

# default test sample amount
if [ -z "$1" ]; then # test if we gave number of tests to run
	echo "Insert number of test samples";
	exit; # argument is needed therefore exit on failure
fi
sample=$1
if [ -z "$2" ]; then # test if this is given
	parser_class="URL_lister" # if nothing given for parser class use this as default
else
	parser_class=$2
fi
echo -e "[\033[32m*\033[0m] \033[3;29m Running $sample tests on\033[0m $parser_class";
date=$(date +%d-%b-%y-%T) # get date
cpu_info=$(cat /proc/cpuinfo | grep -m1 "model name" | cut -d' ' -f5) # get info on the processor
uname=$(uname -rm) # get info os and kernel
parser_module="$(dirname $(pwd))/torrent_api.py" # module containing parser (TODO change here if needed)
url_file="url_x10_kickass_usearch.txt" # file containing urls to parse (TODO change here if needed)
log_path="outJunk/$date"
mkdir -p $log_path 	# make directory to create log files
# initize counters
i=$sample
t_real=0
t_user=0
t_sys=0
while [ $i -ge 1 ] # while i >= 1
do
	echo "Tests left: $i, saving results to $lotgpath/run_$i.txt";
# read the 3 variables from time output of the parser_test_suite program
# time prints to stderr so redirect it to stdout
	read real user sys <<< $((time -p ./parser_test_suite.py $url_file  $parser_module $parser_class "$log_path/run_$i.txt") 2>&1 | cut -d ' ' -f2);
# add times
	t_real=$(echo "$t_real + $real"|bc);
	t_user=$(echo "$t_user + $user"|bc);
	t_sys=$(echo "$t_sys + $sys"|bc);
	echo -e "Results from $i test on $url_file\nReal: $real s\nUser: $user s\nSys: $sys s" >> "$log_path/run_$i.txt"
	i=$(( $i - 1 )); # i++
done
# calculate average values
t_real=$(echo "$t_real / $sample"|bc -l)
t_user=$(echo "$t_user / $sample"|bc -l)
t_sys=$(echo "$t_sys / $sample"|bc -l)

# log info
echo  "Log from  $cpu_info  |  $uname" > "$log_path/time_results.txt"
echo -e "[\033[32m*\033[0m] \033[3;29mAverage Results from $sample tests on $url_file\033[0m\nReal: $t_real s\nUser: $t_user s\nSys: $t_sys s" | tee -a "$log_path/time_results.txt"
echo -e "[\033[32m*\033[0m] \033[3;29mOutput saved to \033[0m $log_path.txt"
