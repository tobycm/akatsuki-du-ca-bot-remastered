#!/bin/bash

location=$1

if [[ $location == "" ]]
then
    location=".venv"
fi

py -m venv $location
