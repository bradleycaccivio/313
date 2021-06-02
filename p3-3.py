#!/usr/bin/env python
import numpy as np
import spidev
from gpiozero import MCP3008
from time import sleep
import math
import sys

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas

import RPi.GPIO as GPIO

import sounddevice as sd

from hx711 import HX711

def getfreq():
    if fsr.value <= 0.125:
        frequency = 261.63
        block = [0, 0, 3, 3]
    elif fsr.value <= 0.25:
        frequency = 293.66
        block = [4, 0, 7, 3]
    elif fsr.value <= 0.375:
        frequency = 329.63
        block = [8, 0, 11, 3]
    elif fsr.value <= 0.5:
        frequency = 349.23
        block = [12, 0, 15, 3]
    elif fsr.value <= 0.625:
        frequency = 392.00
        block = [16, 0, 19, 3]
    elif fsr.value <= 0.75:
        frequency = 440.00
        block = [20, 0, 23, 3]
    elif fsr.value <= 0.875:
        frequency = 493.88
        block = [24, 0, 27, 3]
    else:
        frequency = 523.25
        block = [28, 0, 31, 7]
    return frequency, block

def getvol():
    if pot.value <= 0.125:
        weight = 0.125
        p_c = 1 * 16
    elif pot.value <= 0.25:
        weight = 0.25
        p_c = 3 * 16
    elif pot.value <= 0.375:
        weight = 0.7
        p_c = 5 * 16
    elif pot.value <= 0.5:
        weight = 0.5
        p_c = 7 * 16
    elif pot.value <= 0.625:
        weight = 0.625
        p_c = 9 * 16
    elif pot.value <= 0.75:
        weight = 0.75
        p_c = 11 * 16
    elif pot.value <= 0.875:
        weight = 0.875
        p_c = 13 * 16
    else:
        weight = 1
        p_c = 15 * 16
    return weight, p_c

def getharm():
    hx.power_up()
    val = hx.get_weight(1)
    print(val)
    hx.power_down()
    if val <= 7000:
        return "same"
    elif val <= 14000:
        return "min3"
    elif val <= 21000:
        return "maj3"
    elif val <= 28000:
        return "tritone"
    elif val <= 35000:
        return "perf5"
    else:
        return "min6"
"""
hx = HX711(5,6)
while True:
    try:
        print(getharm())

    except (KeyboardInterrupt, SystemExit):
        print('Cleaning...')
        GPIO.cleanup()
        sys.exit()
"""


harmonics = {
    261.63: {
        "same": [261.63, [0, 4, 3, 7]],     # C
        "maj3": [329.63, [8, 4, 11, 7]],     # 4 semi
        "min3": [311.13, [6, 4, 9, 7]],     # 3 semi
        "perf5": [392.00, [16, 4, 19, 7]],    # 7 semi
        "tritone": [369.99, [14, 4, 17, 7]],  # 6 semi
        "min6": [415.30, [18, 4, 21, 7]]      # 8 semi
    },
    293.66: {
        "same": [293.66, [4, 4, 7, 7]],     # D
        "maj3": [369.99, [14, 4, 17, 7]],     # 4 semi
        "min3": [349.23, [12, 4, 15, 7]],     # 3 semi
        "perf5": [440.00, [20, 4, 23, 7]],    # 7 semi
        "tritone": [415.30, [18, 4, 21, 7]],  # 6 semi
        "min6": [466.16, [22, 4, 25, 7]]      # 8 semi
    },
    329.63: {
        "same": [329.63, [8, 4, 11, 7]],     # E
        "maj3": [415.30, [18, 4, 21, 7]],     # 4 semi
        "min3": [392.00, [16, 4, 19, 7]],     # 3 semi
        "perf5": [493.88, [24, 4, 27, 7]],    # 7 semi
        "tritone": [466.16, [22, 4, 25, 7]],  # 6 semi
        "min6": [523.25, [28, 4, 31, 7]]      # 8 semi
    },
    349.23: {
        "same": [349.23, [12, 4, 15, 7]],     # F
        "maj3": [440.00, [20, 4, 23, 7]],     # 4 semi
        "min3": [415.30, [18, 4, 21, 7]],     # 3 semi
        "perf5": [523.25, [28, 4, 31, 7]],    # 7 semi
        "tritone": [493.88, [24, 4, 27, 7]],  # 6 semi
        "min6": [554.37, [2, 4, 5, 7]]      # 8 semi
    },
    392.00: {
        "same": [392.00, [16, 4, 19, 7]],     # G
        "maj3": [493.88, [24, 4, 27, 7]],     # 4 semi
        "min3": [466.16, [22, 4, 25, 7]],     # 3 semi
        "perf5": [587.33, [4, 4, 7, 7]],    # 7 semi
        "tritone": [554.37, [2, 4, 5, 7]],  # 6 semi
        "min6": [622.25, [6, 4, 9, 7]]      # 8 semi
    },
    440.00: {
        "same": [440.00, [20, 4, 23, 7]],     # A
        "maj3": [554.37, [2, 4, 5, 7]],     # 4 semi
        "min3": [523.25, [28, 4, 31, 7]],     # 3 semi
        "perf5": [659.25, [8, 4, 11, 7]],    # 7 semi
        "tritone": [622.25, [6, 4, 9, 7]],  # 6 semi
        "min6": [698.46, [12, 4, 15, 7]]      # 8 semi
    },
    493.88: {
        "same": [493.88, [24, 4, 27, 7]],     # B
        "maj3": [622.25, [6, 4, 9, 7]],     # 4 semi
        "min3": [587.33, [4, 4, 7, 7]],     # 3 semi
        "perf5": [739.99, [14, 4, 17, 7]],    # 7 semi
        "tritone": [698.46, [12, 4, 15, 7]],  # 6 semi
        "min6": [783.99, [16, 4, 19, 7]]      # 8 semi
    },
    523.25: {
        "same": [523.25, [28, 4, 31, 7]],     # C
        "maj3": [659.25, [8, 4, 11, 7]],     # 4 semi
        "min3": [622.25, [6, 4, 9, 7]],     # 3 semi
        "perf5": [783.99, [16, 4, 19, 7]],    # 7 semi
        "tritone": [739.99, [14, 4, 17, 7]],  # 6 semi
        "min6": [830.61, [18, 4, 21, 7]]      # 8 semi
    }}

weight = 1
p_c = 0
fs = 44100
seconds = 1
b_s = int(fs*seconds)
t = np.linspace(0, seconds, b_s, False)

hx = HX711(5,6)

hx.reset()
hx.tare()
hx.power_down()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.IN)

fsr = MCP3008(5)
pot = MCP3008(0)

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=4, block_orientation=-90)

o_s = sd.OutputStream(samplerate=fs, blocksize=b_s, channels=2, dtype=np.float32)
o_s.start()

while True:
    try:
        #print(getharm())
        frequency, block = getfreq()
            
        weight, p_c = getvol()
        
        if not GPIO.input(25):
            device.contrast(p_c)
            g_h = getharm()
            frequency1 = harmonics[frequency][g_h][0]
            block2 = harmonics[frequency][g_h][1]
            note = np.sin(frequency * t * 2 * np.pi)
            audio = note * (2**15 - 1) / np.max(np.abs(note))
            audio = audio.astype(np.float32)
            note1 = np.sin(frequency1 * t * 2 * np.pi)
            audio1 = note1 * (2**15 - 1) / np.max(np.abs(note))
            audio1 = audio1.astype(np.float32)
            stereo_data = np.column_stack([audio, audio1])
            print('yo')
            print(g_h)
            with canvas(device) as draw:
                draw.rectangle(block, fill="red")
                draw.rectangle(block2, fill="red")
            o_s.write(stereo_data)
            sleep(seconds)
        else:
            device.contrast(0)
            with canvas(device) as draw:
                draw.rectangle(block, fill="red")
            #o_s.write(np.zeros((b_s,2)).astype(np.float32))
                
        device.clear()
    except (KeyboardInterrupt, SystemExit):
        GPIO.cleanup()
        sys.exit()
