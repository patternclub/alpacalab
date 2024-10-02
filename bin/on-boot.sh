#!/bin/bash
cd /home/alpaca
/bin/sleep 2
source /home/alpaca/.bashrc
echo "hmm" > /home/alpaca/test.log
/usr/bin/tmux -vv set-option  -g  default-shell /bin/bash >> tmux_err 2>&1
/usr/bin/tmux -vv new-session -d -A -s stagesesh \; send -t stagesesh "/home/alpaca/alpacalab/bin/start-open-stage-control.sh" ENTER \; detach -s stagesesh >> tmux_err 2>&1
/usr/bin/tmux new-session -d -A -s oscsesh \; send -t oscsesh "/home/alpaca/alpacalab/lights/osc-server.py" ENTER \; detach -s oscsesh >> tmux_err 2>&1
