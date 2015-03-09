#/bin/sh
cd ../prototype
cp instance_config/config_instance_3 config
export PYTHONPATH=$PYTHONPATH:`pwd`
while true
do
    python src/sentinews/tecnonews.py
    sleep 1m
done
