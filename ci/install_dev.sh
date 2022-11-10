#!/bin/bash

# Install dev library
/usr/bin/env pip3 install -r dev-requirements.txt

# Ignore config files
git update-index --skip-worktree config/settings.json
git update-index --skip-worktree config/redis.json