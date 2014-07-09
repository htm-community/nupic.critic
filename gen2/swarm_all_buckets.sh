#!/bin/bash

indices=(0 1 2 3 4 5 6 7 8 9)

for i in "${indices[@]}"
do
    echo "Swarming b${i}..."
    echo "./swarm.py ${1} -p b${i}"
    ./swarm.py ${1} b${i}
done