#! /bin/bash

# Install the required support programs
apt-get install python python-pip python-dev libffi-dev libssl-dev -y
pip2 install setuptools wheel
pip2 install -r requirements.txt
