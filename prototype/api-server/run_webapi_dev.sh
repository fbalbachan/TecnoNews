#!/bin/bash

PID_FILE=./sentilecto-api.pid

if [ -f $PID_FILE ]; then
	PID_TO_KILL=$(cat $PID_FILE)
	if [ -d /proc/$PID_TO_KILL ]; then
		echo Killing pid $PID_TO_KILL
		kill -9 $PID_TO_KILL
	fi
fi

export PYTHONPATH=`pwd`/..
source ../../../bin/activate

cp instances_config/config_instance_dev1 config
{
nohup python api_server.py
} >| nohup.api.out 2>&1 &
