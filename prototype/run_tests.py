export PYTHONPATH=$PYTHONPATH:`pwd`/src
for test in tests/*.py; do python $test; done


