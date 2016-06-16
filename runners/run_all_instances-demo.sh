#!/bin/bash

OLDPWD=`pwd`

cd ~/NaturalEnv/TecnoNews-merge/runners
source ../../bin/activate

truncate "instance.0.out" --size=0
truncate ../prototype/logs/instance0-tecnonews.log --size=0
{
nohup ./run0_demo.sh
} >| "instance.0.out" 2>&1 &

ps -p $! -o pgid | grep -E "[0-9]+" >| instances.pgid

sleep 3
truncate "instance.1.out" --size=0
truncate ../prototype/logs/instance1-tecnonews.log --size=0
{
nohup ./run1_demo.sh
} >| "instance.1.out" 2>&1 &

#ps -p $! -o pgid | grep -E "[0-9]+" >| instance.1.pgid

sleep 3
truncate "instance.2.out" --size=0
truncate ../prototype/logs/instance2-tecnonews.log --size=0
{
nohup ./run2_demo.sh
} >| "instance.2.out" 2>&1 &

#ps -p $! -o pgid | grep -E "[0-9]+" >| instance.2.pgid

#sleep 3
#truncate "instance.3.out" --size=0
#truncate ../prototype/logs/instance3-tecnonews.log --size=0
#{
#nohup ./run3_demo.sh
#} >| "instance.3.out" 2>&1 &

#ps -p $! -o pgid | grep -E "[0-9]+" >| instance.3.pgid

#sleep 3
#truncate "instance.4.out" --size=0
#truncate ../prototype/logs/instance4-tecnonews.log --size=0
#{
#nohup ./run4_demo.sh
#} >| "instance.4.out" 2>&1 &

#ps -p $! -o pgid | grep -E "[0-9]+" >| instance.4.pgid

#sleep 3
#truncate "instance.5.out" --size=0
#truncate ../prototype/logs/instance5-tecnonews.log --size=0
#{
#nohup ./run5_demo.sh
#} >| "instance.5.out" 2>&1 &

#ps -p $! -o pgid | grep -E "[0-9]+" >| instance.5.pgid

cd $OLDPWD
