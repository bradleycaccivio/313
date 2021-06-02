#!/usr/bin/env python
from __future__ import division
import simpleaudio as sa
import numpy as np
import spidev
from gpiozero import MCP3008
from time import sleep
import alsaaudio
import math
import sys

import pyaudio

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import show_message
from luma.core.legacy.font import proportional, LCD_FONT

import RPi.GPIO as GPIO

import sounddevice as sd

#from hx711 import HX711
from hx711 import HX711

print('starting')

hx = HX711(5,6)

hx.reset()
hx.tare()

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.IN)

fsr = MCP3008(5)
pot = MCP3008(0)

o_s = sd.OutputStream(samplerate=44100, blocksize=8820, channels=2, dtype='float32')

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
        weight = 0.2
        p_c = 1 * 16
    elif pot.value <= 0.25:
        weight = 0.45
        p_c = 3 * 16
    elif pot.value <= 0.375:
        weight = 0.7
        p_c = 5 * 16
    elif pot.value <= 0.5:
        weight = 0.95
        p_c = 7 * 16
    elif pot.value <= 0.625:
        weight = 1.2
        p_c = 9 * 16
    elif pot.value <= 0.75:
        weight = 1.45
        p_c = 11 * 16
    elif pot.value <= 0.875:
        weight = 1.70
        p_c = 13 * 16
    else:
        weight = 1.95
        p_c = 15 * 16
    return weight, p_c

def getharm():
    val = hx.get_weight(1)
    print(val)
    if val <= 9000:
        return "same"
    elif val <= 18000:
        return "min3"
    elif val <= 36000:
        return "maj3"
    elif val <= 45000:
        return "tritone"
    elif val <= 56000:
        return "perf5"
    else:
        return "min6"
"""
def callback(outdata, frames, time, status):
    if not GPIO.input(25):
        seconds = 0.2
        t = np.linspace(0, seconds, seconds * fs, False)
        note = np.sin(frequency * t * 2 * np.pi)
        audio = note * (2**15 - 1) / np.max(np.abs(note))
        audio = audio.astype(np.float32)
        frequency1 = harmonics[frequency][getharm()]
        note1 = np.sin(frequency1 * t * 2 * np.pi)
        audio1 = note1 * (2**15 - 1) / np.max(np.abs(note))
        audio1 = audio1.astype(np.float32)
        stereo_data = np.column_stack([audio, audio1])]
        outdata[:] = stereo_data
    else:
        outdata.fill(0)
"""

"""
while True:
    try:
        print(getharm())

    except (KeyboardInterrupt, SystemExit):
        print('Cleaning...')
        GPIO.cleanup()
        sys.exit()

_time = 0
while _time < 1000:
    try:
        hx711 = HX711(
                dout_pin=27,
                pd_sck_pin=17,
                channel='A',
                gain=64
        )

        hx711.reset()
        measures = hx711._read()

    finally:
        GPIO.cleanup()  # always do a GPIO cleanup in your scripts!

    print('hi')
    print(measures)
    _time = _time + 1


p = pyaudio.PyAudio()
volume = 0.5
fs = 44100
duration = 10.0
f1 = 261.63
f2 = 329.63

samples1 = (np.sin(2*np.pi*np.arange(fs*duration)*f1/fs)).astype(np.float32)
samples2 = (np.sin(2*np.pi*np.arange(fs*duration)*f2/fs)).astype(np.float32)

assert samples1.ndim == samples2.ndim
assert samples1.size == samples2.size
s_d = np.column_stack([samples1, samples2])

f_a = []

for i,v in enumerate(samples1):
    f_a.append(v)
    f_a.append(samples2[i])

f_a = np.array(f_a)

stream = p.open(format=pyaudio.paFloat32,
                channels=1,
                rate=fs,
                output=True)

stream.write(volume*samples1)
stream.stop_stream()
stream.close()
p.terminate()
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

#m = alsaaudio.Mixer()
weight = 1
#c_v = m.getvolume()
#print(c_v)

p_c = 0

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=4, block_orientation=-90)

def readadc(adcnum):
    if adcnum > 7 or adcnum < 0:
        return -1
    r = spi_d.xfer2([1, 8 + adcnum << 4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    return data

device.clear()

while True:
    frequency, block = getfreq()
        
    weight, p_c = getvol()
    
    fs = 44100
    seconds = 0.2
    #print(fsr.value)
    #print(pot.value)
    #print(m.getvolume())

    t = np.linspace(0, seconds, seconds * fs, False)

    """
    note = np.sin(frequency * t * 2 * np.pi)
    note1 = np.sin(frequency1 * t * 2 * np.pi)

    audio = note * (2**15 - 1) / np.max(np.abs(note))
    audio = audio.astype(np.int16)
    audio1 = note1 * (2**15 - 1) / np.max(np.abs(note))
    audio1 = audio1.astype(np.int16)

    if frequency == frequency1:
        stereo_data = audio
    else:
        stereo_data = np.column_stack([audio, audio1])
    """
    
    if not GPIO.input(25):
        device.contrast(p_c)
        #play_obj = sa.play_buffer(audio, 1, 2, fs)
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
        """
        if frequency != frequency1:
            note1 = np.sin(frequency1 * t * 2 * np.pi)
            audio1 = note1 * (2**15 - 1) / np.max(np.abs(note))
            audio1 = audio1.astype(np.float32)
            stereo_data = np.column_stack([audio, audio1])
        else:
            stereo_data = audio
        """
        with canvas(device) as draw:
            draw.rectangle(block, fill="red")
        o_s.write(stereo_data)
        #sd.play(stereo_data*weight, 44100)
        #sd.wait()
        #play_obj.wait_done()
    else:
        device.contrast(0)
        with canvas(device) as draw:
            draw.rectangle(block, fill="red")
        #_z = np.zeros(2,8820)
        #_z = _z.astype(np.float32)
        o_s.write(np.zeros(2,8820).astype(np.float32))
            
    device.clear()

    #play_obj = sa.play_buffer(audio, 1, 2, fs)
    
    #if GPIO.input(25):
    #    device.contrast(2*16)
    #    print('yes')
    #else:
    #    device.contrast(14*16)
    #    print('no')
    
    #with canvas(device) as draw:
    #    draw.rectangle(block, fill="red")

    #play_obj.wait_done()
    #device.clear()
