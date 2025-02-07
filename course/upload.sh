#!/bin/bash

echo "uploading for $NAME"

#cp ~/Downloads/picow-v1.24.0-beta2-pimoroni-micropython.uf2 /media/alex/RPI-RP2/picow-v1.24.0-beta2-pimoroni-micropython.uf2
#sleep 3

cp config.py config.py.tmp

sed -i -e "s/alex/$NAME/g" config.py.tmp

mpremote fs cp main.py :main.py
mpremote fs cp config.py.tmp :config.py
mpremote fs cp mycolour.py :mycolour.py

mpremote mip install umqtt.simple
