#!/usr/bin/python3

import liblo, serial, select, argparse, re, json
import paho.mqtt.client as mqtt
import sys
import webcolors

ser = serial.Serial('/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_5573731323135141A191-if00', 115200)

def read_password():
    f = open('/home/alpaca/.mqtt-password', 'r')
    password = f.read().rstrip()
    f.close()
    return(password)

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
mqtt_password = args.password or read_password()
print(mqtt_password)
mqtt_port = 1883

subscribe_topics = ["/click"]

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    for topic in subscribe_topics:
        print("subscribing to " + topic)
        client.subscribe(topic)

def on_message(client, userdata, msg):
    topic = msg.topic
    data = json.loads(msg.payload.decode())
    match topic:
        case "/click":
            n = data['n'] if 'n' in data else 0
            duration = data['duration'] if 'duration' in data else 100
            click(n, duration)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username=mqtt_username, password=mqtt_password)
client.connect(mqtt_host, mqtt_port, 60)

def click_callback(path, args):
    n = args[0]
    duration = args[1]
    click(n, duration)


osc_server.add_method("/click", "ii", click_callback)

timeout = 0.1

while True:
    r, w, e = select.select(
        [osc_server.fileno(), client.socket(), ser],
        [client.socket()] if client.want_write() else [],
        [],
        1
    )

    if client.socket() in r:
        client.loop_read()

    if client.socket() in w:
        client.loop_write()

    client.loop_misc()

    if osc_server.fileno() in r:
        osc_server.recv()

    if ser in r:
        print("serial device says: ", ser.readline())
