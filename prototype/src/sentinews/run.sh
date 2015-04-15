cd /home/nvaras/entinews/prototype
export PYTHONPATH=$PYTHONPATH:`pwd`
export PATH=$PATH:/opt/freeling-3.0/bin
while true
do
    python src/sentinews/tecnonews.py
    sleep 15m
done
