#!/bin/bash
SRVR="root@188.225.86.226"
EXECUTABLE="cmbot_main.py"
TARDIR="/root/bots/chormeister_bot"
ssh $SRVR "mkdir $TARDIR"
scp *.py "requirements.txt" "$SRVR:$TARDIR"
ssh $SRVR << EOF
cd "$TARDIR"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
EOF
bash run.sh
