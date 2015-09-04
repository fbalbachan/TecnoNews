#!/bin/bash

USE_IN_MEMORY_INSTANCES="TRUE"

declare -a SYMBOLIC_INSTANCES
declare -a PS_RECS
declare -a PPIDS
if [[ $# -eq "2" ]]; then
	ACTION="$1"
	SYMBOLIC_INSTANCES=(0 1 2 3 4 6)

	if [[ USE_IN_MEMORY_INSTANCES == "TRUE" ]]; then
		PS_RECS=$(ps -fea | grep "nlt-run" | grep "bin/sh" | grep -E "\./run(.*)\.sh" | grep -v "grep")
	else
		PS_RECS=$(ps -fea | grep "nlt-run" | grep "bin/sh" | grep -E "\./run(0|1|2|3|4|6)\.sh" | grep -v "grep")
	fi

	PPIDS=($(echo "$PS_RECS" | awk '{for (i=1;i<=NF;i++) if (i==2) printf("%s", $i); print ""}'))

elif [[ $# -eq "3" && $false ]]; then
	ACTION="$1"
	SYMBOLIC_INSTANCES=("$2")
	PS_RECS=
	PPIDS=

else
	echo "Usage: "
	echo "  tecnonews-service action [instance_number]"
	echo "where "
	echo "  action: start | stop | restart "
	echo "  instance_number: 0 | 1 | 2 | 3 | 4 | 6"
	echo "                   (if ommitted every instance of \"python src/sentinews/tecnonews.py\""
	echo "                    present in memory will be addressed)"
fi


if [[ "$ACTION" == "restart" ]]; then
	PPIDS_NR=${#PPIDS[@]}
	LAST_IDX=$PPIDS_NR-1
	for i in {0..$LAST_IDX}
	do
		PPID=${PPIDS[$i]}
		PS_REC=${PS_RECS[$i]}
		echo "Killing child processes of PARENT PID = $PPID"
		echo "(ps-entry for parent process --> [$PS_REC])"	
		# pkill -KILL -P $PPID
	done
fi