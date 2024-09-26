#!/usr/bin/python3

import liblo, serial

try:
    osc_server = liblo.Server(7070)
except liblo.ServerError as err:
    print(err)


ser = serial.Serial('/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_5573731323135141A191-if00', 115200)

def rgb_callback(path, args):
    cmd = "%dr%dg%db" % tuple(args)
    ser.write(cmd.encode())

osc_server.add_method("/rgb", "iii", rgb_callback)
    
while True:
    osc_server.recv(100)
