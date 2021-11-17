#!/bin/bash

NET=netstat -tupn | grep 3000
#TOKEN_VAL=`printenv TOKEN`
TOKEN='abcd'

if [ $NET = '']
then
    curl `https://ctf.kewool.net/api/ctf/${TOKEN}`
fi