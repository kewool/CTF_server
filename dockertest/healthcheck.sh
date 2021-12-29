#!/bin/bash

PORT_VAL=`printenv PORT`
TOKEN_VAL=`printenv TOKEN`
HOST_VAL=`printenv HOST`
NET=`netstat -tupn | grep ${PORT_VAL}`

if [ $NET = '']
then
    curl "https://${HOST_VAL}/api/ctf/docker/stop/${TOKEN_VAL}"
fi