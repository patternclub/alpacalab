#!/bin/bash
cd ~/
node open-stage-control -p 6060 --send 127.0.0.1:7070 --read-only --load alpacalab/lights/open-stage-control.json --read-only

