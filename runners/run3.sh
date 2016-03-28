#!/bin/bash

cd ~/NaturalNews-merge/prototype
export PYTHONPATH=$PYTHONPATH:`pwd`
cp instance_config/config_instance_3 config
python src/sentinews/tecnonews.py
