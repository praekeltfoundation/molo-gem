#!/bin/bash

cd $REPO

docker build -t gem-molo .

docker tag -f gem-molo qa-mesos-persistence.za.prk-host.net:5000/gem-molo

docker push qa-mesos-persistence.za.prk-host.net:5000/gem-molo
