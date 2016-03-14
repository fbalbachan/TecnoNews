#!/bin/bash

cd ~/NaturalNews/prototype

source ../bin/activate
export PYTHONPATH=$PYTHONPATH:`pwd`

cp instance_config/config_instance_6 config
python src/sentinews/tecnonews.py
