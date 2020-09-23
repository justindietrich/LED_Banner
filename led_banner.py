#!/usr/bin/python

import sys
import time
import board
import adafruit_dht

import zmq
import RPi.GPIO as GPIO
from time import sleep, strftime
from datetime import datetime

from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, LCD_FONT


# Initial the dht device, with data pin connected to:
dhtDevice = adafruit_dht.DHT22(board.D4)
 
# you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
# This may be necessary on a Linux single board computer like the Raspberry Pi,
# but it will not work in CircuitPython.
# dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)

#  Prepare server context and socket
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
#socket.settimeout(0.00001)

# Setup the Display
serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, width=32, height=8, block_orientation=-90)
device.contrast(50)
virtual = viewport(device, width=32, height=16)
#show_message(device, 'Raspberry Pi MAX7219', fill="white", font=proportional(LCD_FONT), scroll_delay=0.08)


def get_time_and_temp():
    print("get_Time_and_temp")
    # Get the current time
    displaystring = datetime.now().strftime('%A %I:%M %p')
    print(displaystring)

    try: 
        #Try to grab a sensor reading.
        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9/5) +32
        humidity = dhtDevice.humidity

        tempstring = ' {0:0.1f}*  {1:0.1f}%'.format(temperature_f, humidity)
        print(tempstring)
        displaystring = displaystring + tempstring
    
    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        print(error.args[0])
        time.sleep(0.5)
    except Exception as error:
        dhtDevice.exit()
        raise error
    
    print("Displaying message")
    show_message(device, displaystring, fill="white", font=proportional(LCD_FONT), scroll_delay=0.08)

def wait_for_message():
    try:
        # Wait for next request from client
        message = socket.recv()
        # Convert binary data to string
        stringdata = message.decode('utf-8')
        print(stringdata)

        # Send reply back to client. Don't wait for message to finish
        socket.send(b"OK")

        # display message on 7219
        show_message(device, stringdata, fill="white", font=proportional(LCD_FONT), scroll_delay=0.08)
    except socket.timeout as e:
        io =  1
        #print e

get_time_and_temp()

try:
    while True:
        #wait_for_message()
        sleep(1)
        get_time_and_temp()
#        show_message(device, 'Happy Birthday Ella!!', fill="white", font=proportional(LCD_FONT), scroll_delay=0.08)
#        with canvas(virtual) as draw:
#            #text(draw, (0, 1), "Happy Birthday Ella!!", fill="white", font=proportional(CP437_FONT))
#            #text(draw, (0, 1), "Idris", fill="white", font=proportional(CP437_FONT))
#            text(draw, (0, 1), datetime.now().strftime('%I:%M'), fill="white", font=proportional(CP437_FONT))

except KeyboardInterrupt:
    GPIO.cleanup()
