#!/bin/bash

# Setup the test environment


apt-get update
apt-get install python-pip iceweasel xvfb
pip install selenium xvfbwrapper

