#!/bin/bash
cd /apps/entinews/prototype/
export PYTHONPATH=$PYTHONPATH:`pwd`/src:`pwd`/webapp
python webapp/service.py 8321
