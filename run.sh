#!/bin/bash
EXECUTABLE="cmbot_main.py"
pkill -f "$EXECUTABLE"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
nohup python3 "$EXECUTABLE" >/dev/null 2>&1 &
