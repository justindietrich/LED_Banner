#!/usr/bin/python

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

#  Prepare server context and socket
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

# Setup the Display
serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, width=32, height=8, block_orientation=-90)
device.contrast(50)
virtual = viewport(device, width=32, height=16)
#show_message(device, 'Raspberry Pi MAX7219', fill="white", font=proportional(LCD_FONT), scroll_delay=0.08)

# Get the current time
displaystring = datetime.now().strftime('%A %I:%M %p')
print(displaystring)
show_message(device, displaystring, fill="white", font=proportional(LCD_FONT), scroll_delay=0.08)

try:
    while True:
        # Wait for next request from client
        message = socket.recv()
        # Convert binary data to string
        stringdata = message.decode('utf-8')
        print(stringdata)

        # Send reply back to client. Don't wait for message to finish
        socket.send(b"OK")

        # display message on 7219
        show_message(device, stringdata, fill="white", font=proportional(LCD_FONT), scroll_delay=0.08)

#        show_message(device, 'Happy Birthday Ella!!', fill="white", font=proportional(LCD_FONT), scroll_delay=0.08)
#        with canvas(virtual) as draw:
#            #text(draw, (0, 1), "Happy Birthday Ella!!", fill="white", font=proportional(CP437_FONT))
#            #text(draw, (0, 1), "Idris", fill="white", font=proportional(CP437_FONT))
#            text(draw, (0, 1), datetime.now().strftime('%I:%M'), fill="white", font=proportional(CP437_FONT))

except KeyboardInterrupt:
    GPIO.cleanup()
