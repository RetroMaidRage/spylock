#!/bin/bash
username=$(whoami)

cd "$(dirname "$0")"
source /home/$username/venv/bin/activate
python main.py
