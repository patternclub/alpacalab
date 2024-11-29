#!/usr/bin/python3

import liblo, serial, select, argparse, re, json
import paho.mqtt.client as mqtt
import sys
import webcolors

ser = serial.Serial('/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_5573731323135141A191-if00', 115200)

def ser_rgb(c,r,g,b,l,d,strobe):
    if c == strobe_channel:
        cmd = "%dc%dR%dG%dB%dD%dS%dl" % (int(c), int(r), int(g), int(b), int(d), int(strobe), int(l))
    else:
        cmd = "%dc%dr%dg%db%dl" % (int(c), int(r), int(g), int(b), int(l))
    ser.write(cmd.encode())

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

strobe_channel = 3

subscribe_topics = ["/light"]

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    for topic in subscribe_topics:
        print("subscribing to " + topic)
        client.subscribe(topic)

def on_message(client, userdata, msg):
    topic = msg.topic
    data = json.loads(msg.payload.decode())
    match topic:
        case "/light":
            if 'color' in data and data['color']:
                (r, g, b) = webcolors.name_to_rgb(data['color'])
            else:
                r = data['red'] if 'red' in data else 0
                g = data['green'] if 'green' in data else 0
                b = data['blue'] if 'blue' in data else 0
            c = data['channel'] if 'channel' in data else 0
            d = data['d'] if 'd' in data else 100
            l = data['l'] if 'l' in data else 255
            strobe = data['strobe'] if 'strobe' in data else 0
            ser_rgb(c, r, g, b, l, d, strobe)
                

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username=mqtt_username, password=mqtt_password)
client.connect(mqtt_host, mqtt_port, 60)

def rgb_callback(path, args):
    if len(args) == 4:
        c = args[3]
    else:
        m = match(r'/rgb/(\d+)', path)
        if m:
            c = int(m[1])-1
        else:
            c = 0
    ser_rgb(c, args[0], args[1], args[2], 255)

def irgb_callback(path, args):
    c = chr(ord('x')+args[0])
    ser.write(cmd.encode())

osc_server.add_method("/rgb", "iiii", rgb_callback)
osc_server.add_method("/rgb/1", "iii", rgb_callback)
osc_server.add_method("/rgb/2", "iii", rgb_callback)
osc_server.add_method("/rgb/3", "iii", rgb_callback)
osc_server.add_method("/rgb/4", "iii", rgb_callback)

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
        print("arduino says: ", ser.readline())
