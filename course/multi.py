import plasma
from plasma import plasma2040
import network
import time
import requests
import ujson

from umqtt.simple import MQTTClient
from mycolour import hsv_to_rgb, colour_names
from inventor import Inventor2040W

NAME = "alex"

board = Inventor2040W()

# Total number of LEDs on our LED strip
NUM_LEDS = 66

# How long between cheerslight updates in seconds
INTERVAL = 60

mqtt_server = "slab.org"
mqtt_user = "alpaca"
mqtt_pass = "dorkface"

#mqtt_server = "sponge.algorithmicpattern.org"
#mqtt_user = "alex"
#mqtt_pass = "betweenyourtoes"


status = {}

# Check and import the SSID and Password from secrets.py
try:
    from secrets import WIFI_SSID, WIFI_PASSWORD
    if WIFI_SSID == "":
        raise ValueError("WIFI_SSID in 'secrets.py' is empty!")
    if WIFI_PASSWORD == "":
        raise ValueError("WIFI_PASSWORD in 'secrets.py' is empty!")
except ImportError:
    raise ImportError("'secrets.py' is missing from your Plasma 2350 W!")
except ValueError as e:
    print(e)

network.hostname(NAME)
wlan = network.WLAN(network.STA_IF)


def connect():
    # Connect to the network specified in secrets.py
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while wlan.isconnected() is False:
        print("Attempting connection to {}".format(WIFI_SSID))
        time.sleep(1)


# APA102 / DotStar™ LEDs
# led_strip = plasma.APA102(NUM_LEDS, 0, 0, plasma2040.DAT, plasma2040.CLK)

# WS2812 / NeoPixel™ LEDs
# led_strip = plasma.WS2812(NUM_LEDS, 0, 0, plasma2040.DAT, color_order=plasma.COLOR_ORDER_BGR)
led_strip = None

# Start connection to the network
connect()

# Store the local IP address
ip_addr = wlan.ipconfig('addr4')[0]

# Let the user know the connection has been successful
# and display the current IP address of the Plasma 2350 W
print("Successfully connected to {}. Your Plasma 2350 W's IP is: {}".format(WIFI_SSID, ip_addr))

color = (255,255,255)

last = time.ticks_ms()

def sub_cb(topic, s_msg):
    global color, last
    topic = topic.decode('ASCII')
    # print(topic)
    if led_strip and (topic == "/light/all" or topic == "/light/" + NAME):
        msg = ujson.loads(s_msg)
        if 'light' in msg:
            light = msg['light']
            color = (0,0,0)
            if 'color' in msg and msg['color'] in colour_names:
                x = colour_names[msg['color']]
                color = (x[0], x[1], x[2])
            elif 'hue' in msg and 'sat' in msg and 'val' in msg:
                color = hsv_to_rgb((msg['hue'], msg['sat'], msg['val']))
            elif 'red' in msg and 'green' in msg and 'blue' in msg:
                color = (msg['red']*255.0, msg['green']*255.0, msg['blue']*255.0)
            status[light] = color
            led_strip.set_rgb(int(light), *color)
    elif topic == "/move/all" or topic == "/move/" + NAME:
        msg = ujson.loads(s_msg)
        # print(msg)
        if 'by' in msg:
            motor = msg['motor'] or 0
            by = msg['by']
            #print(by)
            s = board.servos[motor]
            s.value(by)
            foo = time.ticks_ms()
            print(foo-last)
            last = foo
            
            

mqtt = MQTTClient(NAME, mqtt_server, user=mqtt_user, password=mqtt_pass)
mqtt.set_callback(sub_cb)

mqtt.connect()
mqtt.subscribe("/light/all")
mqtt.subscribe("/light/" + NAME)
mqtt.subscribe("/move/all")
mqtt.subscribe("/move/" + NAME)

print("Connected to %s mqtt server" % (mqtt_server,))
mqtt.set_callback(sub_cb)

if led_strip:
    # Start updating the LED strip
    led_strip.start()

while True:
    if wlan.isconnected():
        try:
            mqtt.wait_msg()
        except OSError:
            print("OS Error!")
    else:
        print("Lost connection to network {}".format(WIFI_SSID))
        time.sleep(10);
    mqtt.check_msg()

print("oh!")
