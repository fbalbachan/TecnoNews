#!/bin/bash

if [ "$1" = "stop" -o "$1" = "restart" ]
then
    PID_FILE=./sentilecto-api.pid
    PID_TO_KILL=$(cat $PID_FILE)

    if [ -f $PID_FILE ]
    then
        if [ -d /proc/$PID_TO_KILL ]; then
            echo Killing pid $PID_TO_KILL
            kill -9 $PID_TO_KILL
        fi
    fi
fi

if [ "$1" = "start" -o "$1" = "restart" ]
then
    export PYTHONPATH=`pwd`/..
    source ../../../bin/activate

    cp instances_config/config_instance_demo config
    nohup python api_server.py > nohup.api.out 2>&1 &
fi
