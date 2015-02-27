cd ../prototype
export PYTHONPATH=$PYTHONPATH:`pwd`
while true
do
    python src/sentinews/tecnonews.py
    sleep 1m
done
