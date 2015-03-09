#/bin/sh
cd ../prototype
export PYTHONPATH=$PYTHONPATH:`pwd`
while true
do
    cp instance_config/config_instance_3 config
    python src/sentinews/tecnonews.py
    sleep 1m
done
