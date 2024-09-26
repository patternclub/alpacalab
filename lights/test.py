#!/usr/bin/python3
import liblo,time

target = liblo.Address('localhost', 7070)

liblo.send(target, '/rgb', 255,255,255)
time.sleep(0.5)
liblo.send(target, '/rgb', 0,0,0)

