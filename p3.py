#!/usr/bin/python

import spidev
import time

import RPi.GPIO as GPIO

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import show_message
from luma.core.legacy.font import proportional, LCD_FONT

block1 = [0, 0, 7, 7]
block1_t = [0, 0, 0, 7]
block2 = [24, 0, 31, 7]
block2_t = [24, 0, 31, 7]

block3 = [8, 0, 15, 7]
block3_t = [8, 0, 15, 7]
block4 = [16, 0, 23, 7]

delay = 0.05
volume_channel = 0
pitch_channel = 7
curr_chord = None
perc_i = 0

spi_d = spidev.SpiDev()
spi_d.open(0, 0)

spi_d.max_speed_hz = 1000000

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=4, block_orientation=-90)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.IN)
GPIO.setup(21, GPIO.IN)

def readadc(adcnum):
    if adcnum > 7 or adcnum < 0:
        return -1
    r = spi_d.xfer2([1, 8 + adcnum << 4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    return data

def getintensity(pad_value):
    if pad_value < 250:
        return None
    elif pad_value < 450:
        return 0
    elif pad_value < 550:
        return 1
    elif pad_value < 650:
        return 2
    elif pad_value < 700:
        return 3
    elif pad_value < 750:
        return 4
    elif pad_value < 800:
        return 5
    elif pad_value < 850:
        return 6
    else:
        return 7

try:
    while True:
        if not GPIO.input(25) and perc_i == 0:
            perc_i = 7
            block3_t[3] = perc_i
            block3_t[2] = block3[2] - (7-perc_i)
        else:
            perc_i = perc_i - 1
            if perc_i <= 0:
                perc_i = 0
            block3_t[3] = perc_i
            block3_t[2] = block3[2] - (7-perc_i)
        if not GPIO.input(21):
            if curr_chord is None:
                curr_chord = 0
            elif curr_chord == 7:
                curr_chord = None
            else:
                curr_chord = curr_chord + 1
            block1_t[0] = curr_chord
            block1_t[2] = curr_chord
        volume_value = readadc(volume_channel)
        pitch_value = readadc(pitch_channel)
        _i = getintensity(volume_value)
        _j = getintensity(pitch_value)
        if _j is None:
            _j = 0
        if (_i is None):
            device.contrast(8*16)
            with canvas(device) as draw:
                block2_t[3] = -1
                draw.rectangle(block2, fill="black")
                if curr_chord is None:
                    draw.rectangle(block1, fill="black")
                else:
                    draw.rectangle(block1_t, fill="red")
                if perc_i:
                    draw.rectangle(block3_t, fill="red")
                else:
                    draw.rectangle(block3, fill="black")
                draw.rectangle(block4, fill="black")
            time.sleep(delay)
        
        else:
            if curr_chord is None:
                device.contrast(8*16)
            elif _j == block1_t[0]:
                device.contrast(15*16)
            else:
                device.contrast(4*15)
            block2_t[3] = _i
            block2_t[0] = block2[0] + _j
            block2_t[2] = block2[0] + _j
            with canvas(device) as draw:
                draw.rectangle(block2_t, fill="red")
                if curr_chord is None:
                    draw.rectangle(block1, fill="black")
                else:
                    draw.rectangle(block1_t, fill="red")
                if perc_i:
                    draw.rectangle(block3_t, fill="red")
                else:
                    draw.rectangle(block3, fill="black")
                draw.rectangle(block4, fill="black")
            time.sleep(delay)
        device.clear()
except KeyboardInterrupt:
    pass
