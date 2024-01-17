#!/bin/bash

# prepare the evaluation
# re-validate login information
rm -rf agentboard/.auth
mkdir -p agentboard/.auth
python3 agentboard/environment/browser_env/auto_login.py --auth_folder agentboard/.auth
