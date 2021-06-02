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

print('starting')



def getfreq():
    if fsr.value <= 0.125:
        frequency = 261.63
        block = [0, 0, 3, 7]
    elif fsr.value <= 0.25:
        frequency = 293.66
        block = [4, 0, 7, 7]
    elif fsr.value <= 0.375:
        frequency = 329.63
        block = [8, 0, 11, 7]
    elif fsr.value <= 0.5:
        frequency = 349.23
        block = [12, 0, 15, 7]
    elif fsr.value <= 0.625:
        frequency = 392.00
        block = [16, 0, 19, 7]
    elif fsr.value <= 0.75:
        frequency = 440.00
        block = [20, 0, 23, 7]
    elif fsr.value <= 0.875:
        frequency = 493.88
        block = [24, 0, 27, 7]
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
    val = hx.get_weight(1)
    print(val)
    if val <= 12000:
        return "same"
    elif val <= 24000:
        return "min3"
    elif val <= 36000:
        return "maj3"
    elif val <= 48000:
        return "tritone"
    elif val <= 60000:
        return "perf5"
    else:
        return "min6"

"""
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
        "same": 261.63,     # C
        "maj3": 329.63,     # 4 semi
        "min3": 311.13,     # 3 semi
        "perf5": 392.00,    # 7 semi
        "tritone": 369.99,  # 6 semi
        "min6": 415.30      # 8 semi
    },
    293.66: {
        "same": 293.66,     # D
        "maj3": 369.99,     # 4 semi
        "min3": 349.23,     # 3 semi
        "perf5": 440.00,    # 7 semi
        "tritone": 415.30,  # 6 semi
        "min6": 466.16      # 8 semi
    },
    329.63: {
        "same": 329.63,     # E
        "maj3": 415.30,     # 4 semi
        "min3": 392.00,     # 3 semi
        "perf5": 493.88,    # 7 semi
        "tritone": 466.16,  # 6 semi
        "min6": 523.25      # 8 semi
    },
    349.23: {
        "same": 349.23,     # F
        "maj3": 440.00,     # 4 semi
        "min3": 415.30,     # 3 semi
        "perf5": 523.25,    # 7 semi
        "tritone": 493.88,  # 6 semi
        "min6": 554.37      # 8 semi
    },
    392.00: {
        "same": 392.00,     # G
        "maj3": 493.88,     # 4 semi
        "min3": 466.16,     # 3 semi
        "perf5": 587.33,    # 7 semi
        "tritone": 554.37,  # 6 semi
        "min6": 622.25      # 8 semi
    },
    440.00: {
        "same": 440.00,     # A
        "maj3": 554.37,     # 4 semi
        "min3": 523.25,     # 3 semi
        "perf5": 659.25,    # 7 semi
        "tritone": 622.25,  # 6 semi
        "min6": 698.46      # 8 semi
    },
    493.88: {
        "same": 493.88,     # B
        "maj3": 622.25,     # 4 semi
        "min3": 587.33,     # 3 semi
        "perf5": 739.99,    # 7 semi
        "tritone": 698.46,  # 6 semi
        "min6": 783.99      # 8 semi
    },
    523.25: {
        "same": 523.25,     # C
        "maj3": 659.25,     # 4 semi
        "min3": 622.25,     # 3 semi
        "perf5": 783.99,    # 7 semi
        "tritone": 739.99,  # 6 semi
        "min6": 830.61      # 8 semi
    }}

weight = 1
p_c = 0
fs = 44100
seconds = 0.2
t = np.linspace(0, seconds, seconds * fs, False)

hx = HX711(5,6)

hx.reset()
hx.tare()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.IN)

fsr = MCP3008(5)
pot = MCP3008(0)

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=4, block_orientation=-90)

o_s = sd.OutputStream(samplerate=fs, blocksize=fs*seconds, channels=2, dtype=np.float32)
o_s.start()

while True:
    frequency, block = getfreq()
        
    weight, p_c = getvol()
    
    if not GPIO.input(25):
        device.contrast(p_c)
        frequency1 = harmonics[frequency][getharm()]
        note = np.sin(frequency * t * 2 * np.pi)
        audio = note * (2**15 - 1) / np.max(np.abs(note))
        audio = audio.astype(np.float32)
        note1 = np.sin(frequency1 * t * 2 * np.pi)
        audio1 = note1 * (2**15 - 1) / np.max(np.abs(note))
        audio1 = audio1.astype(np.float32)
        stereo_data = np.column_stack([audio, audio1])
        print('yo')
        print(stereo_data.shape)
        with canvas(device) as draw:
            draw.rectangle(block, fill="red")
        o_s.write(stereo_data)
    else:
        device.contrast(0)
        with canvas(device) as draw:
            draw.rectangle(block, fill="red")
        _z = np.zeros((fs*seconds,2))
        _z = _z.astype(np.float32)
        print('hi')
        print(_z.shape)
        o_s.write(np.zeros((fs*seconds,2)).astype(np.float32))
            
    device.clear()
