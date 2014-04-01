#!/bin/bash
cd /apps/entinews/prototype/
export PYTHONPATH=$PYTHONPATH:`pwd`/src:`pwd`/webapp

RUNNING_PID=$(ps -ef|grep "root"| grep "python webapp/service.py 8321"|cut -d' '  -f6)
[[ -n $RUNNING_PID ]] && kill -9 $RUNNING_PID

python webapp/service.py 8321
