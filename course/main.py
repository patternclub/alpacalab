import plasma
from plasma import plasma2040
import network
import time
import requests
import ujson
import ubinascii

from umqtt.simple import MQTTClient
from mycolour import hsv_to_rgb, colour_names
from inventor import Inventor2040W

from config import name, wifis, mqtt_server, mqtt_user, mqtt_pass

print("hello, I'm ", name)

board = Inventor2040W()

# Total number of LEDs on our LED strip
NUM_LEDS = 50

network.hostname(name)

wlan = network.WLAN(network.STA_IF)



def connect():
    global ip_addr, mac
    # Connect to the network specified in secrets.py
    wlan.active(True)
    print("scanning...")
    found = wlan.scan()
    wifi_name = ""
    connected = False
    for w in found:
        wifi_name = w[0].decode('ascii')
        if wifi_name in wifis:
            wlan.connect(wifi_name, wifis[wifi_name])
            while wlan.isconnected() is False:
                print("Attempting connection to {}".format(wifi_name))
                time.sleep(1)
            connected = True
            break

    if connected:
        ip_addr = wlan.ipconfig('addr4')[0]
        print(ip_addr)
        mac = ubinascii.hexlify(wlan.config('mac')).decode()
        print("Successfully connected to {}. Your Plasma 2350 W's IP is: {} mac is: {}".format(wifi_name, ip_addr, mac))



# APA102 / DotStar™ LEDs
# led_strip = plasma.APA102(NUM_LEDS, 0, 0, plasma2040.DAT, plasma2040.CLK)

# WS2812 / NeoPixel™ LEDs
led_strip = plasma.WS2812(NUM_LEDS, 0, 0, plasma2040.DAT, color_order=plasma.COLOR_ORDER_RGB)
#led_strip = None

# Start connection to the network
connect()

color = (255,255,255)

timeoff = {}

def check_timeoffs():
    for light, value in timeoff.items():
        if time.ticks_diff(value, time.ticks_ms()) < 0:
            led_strip.set_rgb(int(light), *(0,0,0))
            del timeoff[light]

def light_on(light, color, msg):
    led_strip.set_rgb(light, *color)
    if 'duration' in msg and 'blink' in msg and msg["blink"]:
        # Add 20ms to allow for processing delay, to avoid switching off between
        # contiguous events
        t = time.ticks_add(int(time.ticks_ms()), int(msg["duration"]*1000) + 20)
        timeoff[light] = t


def sub_cb(topic, s_msg):
    global color, last
    topic = topic.decode('ASCII')
    if led_strip and (topic == "/light/all" or topic == "/light/" + name):
        msg = ujson.loads(s_msg)
        if 'light' in msg:
            light = msg['light']
            color = (0,0,0)
            if 'color' in msg and msg['color'] in colour_names:
                x = colour_names[msg['color']]
                color = (x[0], x[1], x[2])
            elif 'hue' in msg:
                color = hsv_to_rgb((msg['hue'], msg.get('saturation', 1), msg.get('brightness', 1)))
            elif 'red' in msg and 'green' in msg and 'blue' in msg:
                color = (msg['red']*255.0, msg['green']*255.0, msg['blue']*255.0)
            if int(light) == -1:
                for i in range(0, NUM_LEDS):
                    light_on(i, color, msg)
            else:
                light_on(int(light), color, msg)
    elif topic == "/move/all" or topic == "/move/" + name:
        msg = ujson.loads(s_msg)
        if 'move' in msg:
            motor = msg['motor'] or 0
            move = msg['move']
            s = board.servos[motor]
            s.value(move)
            

mqtt = MQTTClient(name, mqtt_server, user=mqtt_user, password=mqtt_pass)
mqtt.set_callback(sub_cb)

mqtt.connect()
mqtt.subscribe("/light/all")
mqtt.subscribe("/light/" + name)
mqtt.subscribe("/move/all")
mqtt.subscribe("/move/" + name)

print("Connected to %s mqtt server" % (mqtt_server,))
mqtt.set_callback(sub_cb)

mqtt.publish("/hello", "%s is here, with ip address %s and mac %s" % (name, ip_addr, mac))

if led_strip:
    # Start updating the LED strip
    led_strip.start()
    led_strip.set_rgb(0, *color)

while True:
    if wlan.isconnected():
        try:
            mqtt.check_msg()
        except OSError:
            print("OS Error!")
    else:
        print("Lost connection to network {}".format(WIFI_SSID))
        time.sleep(3);
    # mqtt.check_msg()
    check_timeoffs()
    # give the cpu a rest
    #time.sleep(0.005)

        

print("oh!")

