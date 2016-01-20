#!/bin/bash

ACTION=$1

OLDPWD=`pwd`

DEMOROOT="$HOME/NaturalEnv/TecnoNews/prototype/webapp"
cd "$DEMOROOT"

PID_FILE="./sentilecto.pid"
PID_TO_KILL=$(cat "$PID_FILE")

if [ "$ACTION" = "stop" -o "$ACTION" = "restart" ]; then

    kill -9 "$PID_TO_KILL"

fi

if [ "$ACTION" = "start" -o "$ACTION" = "restart" ]; then

    if [ -f "$PID_FILE" ]; then
        if [ -d "/proc/$PID_TO_KILL" ]; then
            echo Killing pid "$PID_TO_KILL"
            kill -9 "$PID_TO_KILL"
        fi
    fi

    source $HOME/NaturalEnv/bin/activate
    export PYTHONPATH="$PYTHONPATH:..:."

    cp ../instance_config/config_instance_demo_dev ../config

    {
        nohup python -u service.py 8321
    } >| nohup.demo.out &

fi

cd $OLDPWD
