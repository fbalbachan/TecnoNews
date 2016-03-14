#!/bin/bash

if [ "$1" == "stop" -o "$1" == "restart" ]
then
    if [ "$USER" == "nlt-runner" ]; then
        killall -9 -u "nlt-runner" python
    fi
fi


if [ "$1" == "start" -o "$1" == "restart" ]
then
    OLDPWD=`pwd`

    cd ~/NaturalNews/runners
    source ../bin/activate

    for i in {0..5}
    do  
        truncate "instance.$i.out" --size=0
        truncate "../prototype/logs/instance-$i-tecnonews.log" --size=0
        {
        nohup "./run$i.sh"
        } >| "instance.$i.out" 2>&1 &

        sleep 3
    done

    cd $OLDPWD
fi
