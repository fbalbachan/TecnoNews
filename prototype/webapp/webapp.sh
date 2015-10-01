#!/bin/bash

ACTION=$1

if [ $ACTION -eq "stop" -or $ACTION -eq "restart" ]; then

    kill -9 $(cat ./sentilecto.pid)

fi

if [ $ACTION -eq "start" -or $ACTION -eq "restart" ]; then

    cd $HOME/NaturalEnv/TecnoNews/prototype/webapp

    PID_FILE=./sentilecto.pid
    if [ -f $PID_FILE ]; then
        PID_TO_KILL=$(cat $PID_FILE)
        if [ -d /proc/$PID_TO_KILL ]; then
            echo Killing pid $PID_TO_KILL
            kill -9 $PID_TO_KILL
        fi
    fi

    source $HOME/NaturalEnv/bin/activate
    export PYTHONPATH=$PYTHONPATH:..:.

    cp ../instance_config/config_instance_dev ../config

    {
        nohup python2.7 service.py 8321
    } >| nohup.demo.out &

fi

