#!/bin/bash


if [ "$1" = "restart" ]
then

	cd ~/NaturalEnv

	source bin/activate

	cd NaturalNews

	git pull

	cd prototype/webapp

	./stop_webapp.sh

	nohup ./run_webapp.sh &
fi
