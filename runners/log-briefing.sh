#!/bin/bash

ID=$1

grep -B 25 -n "Error: " nohup.$ID.out > ./briefings/$ID.errors.txt
grep -B 25 -n "Exception: " nohup.$ID.out > ./briefings/$ID.exceptions.txt 
grep ", line " nohup.$ID.out | sort -u > ./briefings/$ID.errors-lines.txt

grep "Exception: " nohup.$ID.out | sort -u > ./briefings/$ID.exceptions-briefing.txt
grep "Error: " nohup.$ID.out | sort -u > ./briefings/$ID.errors-briefing.txt

