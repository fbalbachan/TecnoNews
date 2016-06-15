#!/bin/bash

cd ~/NaturalEnv/TecnoNews-merge/prototype

source ../../bin/activate
export PYTHONPATH=/usr/lib/python2.7/site-packages:/usr/lib/python2.7/dist-packages:$PYTHONPATH:`pwd`

cp instance_config/config_instance_0_demo config
python src/sentinews/tecnonews.py
