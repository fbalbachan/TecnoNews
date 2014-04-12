#!/bin/bash
export PYTHONPATH=`pwd`/..
echo $PYTHONPATH

PID_FILE=/tmp/entinews.pid
if [ -f $PID_FILE ]; then
	PID_TO_KILL=$(cat $PID_FILE)
	if [ -d /proc/$PID_TO_KILL ]; then
		echo Killing pid $PID_TO_KILL
		kill -9 $PID_TO_KILL
	fi
fi

python service.py 8321
