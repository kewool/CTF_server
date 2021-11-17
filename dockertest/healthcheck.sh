#!/bin/bash

NET=netstat -tupn | grep 3000

echo ${NET}