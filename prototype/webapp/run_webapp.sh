#!/bin/bash

PID_FILE=/tmp/entinews.pid
if [ -f $PID_FILE ]; then
	PID_TO_KILL=$(cat $PID_FILE)
	if [ -d /proc/$PID_TO_KILL ]; then
		echo Killing pid $PID_TO_KILL
		kill -9 $PID_TO_KILL
	fi
fi

source $HOME/NaturalEnv/bin/activate
export PYTHONPATH=$PYTHONPATH:$HOME/NaturalEnv/NaturalNews/prototype/:$HOME/NaturalEnv/NaturalNews/prototype/webapp

python2.7 service.py 8321
