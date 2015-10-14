#!/bin/bash

ACTION=$1

if [ "$ACTION" = "stop" -o "$ACTION" = "restart" ]; then

    kill -9 $(cat ./sentialexis.pid)

fi

if [ "$ACTION" = "start" -o "$ACTION" = "restart" ]; then

    cd $HOME/NaturalEnv/TecnoNews/prototype/webapp

    PID_FILE=./sentialexis.pid
    if [ -f $PID_FILE ]; then
        PID_TO_KILL=$(cat $PID_FILE)
        if [ -d /proc/$PID_TO_KILL ]; then
            echo Killing pid $PID_TO_KILL
            kill -9 $PID_TO_KILL
        fi
    fi

    source $HOME/NaturalEnv/bin/activate
    export PYTHONPATH=$PYTHONPATH:..:.

    cp ../instance_config/config_instance_dev2 ../config

    {
        nohup python service.py 8323
    } >| nohup.demo.out &

fi

