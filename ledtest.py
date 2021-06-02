from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.led_matrix.device import max7219

import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(12, GPIO.IN)
GPIO.setup(16, GPIO.IN)

serial = spi(port=0, device=0, gpio=noop(), block_orientation=-90)
device = max7219(serial, width=32, height=8)
box1 = [0, 0, 7, 7]
box2 = [8, 0, 15, 7]
box3 = [16, 0, 23, 7]
box4 = [24, 0, 31, 7]

with canvas(device) as draw:
    #draw.rectangle(box1, fill="red")
    draw.text((0, -3), "X", fill="red")
    draw.text((16, -3), "X", fill="red")
    draw.rectangle(box2, fill="red")
    draw.rectangle(box4, fill="red")
time.sleep(1)
with canvas(device) as draw:
    #draw.rectangle(box1, fill="red")
    draw.text((8, -3), "X", fill="red")
    draw.text((24, -3), "X", fill="red")
    draw.rectangle(box1, fill="red")
    draw.rectangle(box3, fill="red")
time.sleep(1)
with canvas(device) as draw:
    #draw.rectangle(box1, fill="red")
    draw.text((0, -3), "X", fill="red")
    draw.text((16, -3), "X", fill="red")
    draw.rectangle(box2, fill="red")
    draw.rectangle(box4, fill="red")
time.sleep(1)
with canvas(device) as draw:
    #draw.rectangle(box1, fill="red")
    draw.text((8, -3), "X", fill="red")
    draw.text((24, -3), "X", fill="red")
    draw.rectangle(box1, fill="red")
    draw.rectangle(box3, fill="red")
time.sleep(1)

while True:
    if not GPIO.input(12) and not GPIO.input(16):
        with canvas(device) as draw:
                draw.rectangle(box1, fill="red")
                draw.rectangle(box4, fill="red")
    elif not GPIO.input(12):
        with canvas(device) as draw:
                draw.rectangle(box1, fill="red")
    elif not GPIO.input(16):
        with canvas(device) as draw:
                draw.rectangle(box4, fill="red")
    else:
        with canvas(device) as draw:
                draw.rectangle(box1, fill="black")
                draw.rectangle(box4, fill="black")
                