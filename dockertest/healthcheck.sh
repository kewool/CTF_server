#!/bin/bash

PORT_VAL=`printenv PORT`
NET=`netstat -tupn | grep ${PORT_VAL}`
TOKEN_VAL=`printenv TOKEN`

if [ $NET = '']
then
    curl "https://ctf.kewool.net/api/ctf/docker/stop/${TOKEN_VAL}"
fi