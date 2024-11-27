#!/usr/bin/python3

import liblo, serial

try:
    osc_server = liblo.Server(7070)
except liblo.ServerError as err:
    print(err)


ser = serial.Serial('/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_5573731323135141A191-if00', 115200)

def rgb_callback(path, args):
    c = 'x'
    if path == "/rgb/2":
        c = 'y'
    if path == "/rgb/3":
        c = 'z'
    
    cmd = "%s%dr%dg%db" % (c, args[0], args[1], args[2])
    ser.write(cmd.encode())

def irgb_callback(path, args):
    c = chr(ord('x')+args[0])
    ser.write(cmd.encode())

osc_server.add_method("/rgb/1", "iii", rgb_callback)
osc_server.add_method("/rgb/2", "iii", rgb_callback)
osc_server.add_method("/rgb/3", "iii", rgb_callback)
    
while True:
    osc_server.recv(100)
