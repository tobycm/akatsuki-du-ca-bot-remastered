#!/usr/bin/bash

if [ -d ".venv" ]; then
    .venv/bin/python3 main.py
else
    python3 main.py
fi
