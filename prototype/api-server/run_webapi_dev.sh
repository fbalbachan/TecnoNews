#!/bin/bash

export PYTHONPATH=`pwd`/..

PID_FILE=./sentilecto-api.pid
if [ -f $PID_FILE ]; then
	PID_TO_KILL=$(cat $PID_FILE)
	if [ -d /proc/$PID_TO_KILL ]; then
		echo Killing pid $PID_TO_KILL
		kill -9 $PID_TO_KILL
	fi
fi

cp config_instances/config_instance_dev1 config
python2.7 api_server.py
