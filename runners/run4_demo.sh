#!/bin/bash

cd ~/NaturalEnv/TecnoNews-merge/prototype

source ../../bin/activate
export PYTHONPATH=$PYTHONPATH:`pwd`
cp instance_config/config_instance_4_demo config
python src/sentinews/tecnonews.py
