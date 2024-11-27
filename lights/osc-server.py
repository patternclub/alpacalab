#!/usr/bin/python3

import liblo, serial, select, argparse, re
import paho.mqtt.client as mqtt
import sys


ser = serial.Serial('/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_5573731323135141A191-if00', 115200)

def ser_rgb(c,r,g,b):
    cmd = "%s%dr%dg%db" % (c, int(r), int(g), int(b))
    ser.write(cmd.encode())

try:
    osc_server = liblo.Server(7070)
except liblo.ServerError as err:
    print(err)
    sys.exit(-1)

parser=argparse.ArgumentParser()
parser.add_argument("--host")
parser.add_argument("--port")
parser.add_argument("--username")
parser.add_argument("--password")
args=parser.parse_args()

mqtt_host = args.host or "sponge"
mqtt_username = args.username or "alex"
mqtt_password = args.password
mqtt_port = 1883

subscribe_topics = ["/light"]

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    for topic in subscribe_topics:
        print("subscribing to " + topic)
        client.subscribe(topic)

def on_message(client, userdata, msg):
    topic = msg.topic
    data = msg.payload.decode()
    match topic:
        case "/light":
            m = re.match("(\d+) (\d+) (\d+) (\d+)", data)
            if m:
                c, r, g, b = m.groups()
                c = chr(ord('x')+int(c))
                ser_rgb(c, r, g, b)
                

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.username_pw_set(username=mqtt_username, password=mqtt_password)
mqttc.connect(mqtt_host, mqtt_port, 60)

def rgb_callback(path, args):
    c = 'x'
    if path == "/rgb/2":
        c = 'y'
    if path == "/rgb/3":
        c = 'z'
    ser_rgb(c, args[0], args[1], args[2])

def irgb_callback(path, args):
    c = chr(ord('x')+args[0])
    ser.write(cmd.encode())

osc_server.add_method("/rgb/1", "iii", rgb_callback)
osc_server.add_method("/rgb/2", "iii", rgb_callback)
osc_server.add_method("/rgb/3", "iii", rgb_callback)

timeout = 0.1

while True:
    readable, writeable, exceptional = select.select([osc_server.fileno(), mqttc.socket()], [],[], timeout)
    for sock in readable:
        if sock == osc_server.fileno():
            osc_server.recv()
        if sock == mqttc.socket():
            rc = mqttc.loop_read()
            rc = mqttc.loop_misc()
            if rc != 0:
                print("mqtt error")
                sys.exit(-2)
            while mqttc.want_write():
                rc = mqttc.loop_write()
                if rc != 0:
                    print("mqtt error")
                    sys.exit(-2)
