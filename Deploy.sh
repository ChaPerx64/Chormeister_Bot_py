#!/bin/bash
SRVR="root@188.225.86.226"
EXECUTABLE="cmbot_main.py"
TARDIR="/root/bots/chormeister_bot"
ssh $SRVR "mkdir $TARDIR"
scp *.py "requirements.txt" "$SRVR:$TARDIR"
ssh $SRVR << EOF
pkill -f "$EXECUTABLE"
cd "$TARDIR"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
nohup python3 "$EXECUTABLE" >/dev/null 2>&1 &
EOF
