#!/bin/bash

location=$1

if [[ $location == "" ]]
then
    location=".venv"
fi

python3 -m venv $location
