#!/bin/bash
EXECUTABLE="cmbot_main.py"
TARDIR="/root/bots/chormeister_bot"
pkill -f "$EXECUTABLE"
cd "$TARDIR"
python3 -m venv venv
source venv/bin/activate
nohup python3 "$EXECUTABLE" >/dev/null 2>&1 &
