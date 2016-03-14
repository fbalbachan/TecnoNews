#!/bin/bash

cd ~/NaturalNews/prototype
export PYTHONPATH=$PYTHONPATH:`pwd`
cp instance_config/config_instance_4 config
python src/sentinews/tecnonews.py
