#!/bin/bash

location=$1

if [[ $location == "" ]]
then
    location=".venv"
fi

echo
echo
echo "Run this command to activate venv:"
echo
echo "source $location/bin/activate"
