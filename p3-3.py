#!/usr/bin/env python
from __future__ import division
import simpleaudio as sa
import numpy as np
import spidev
from gpiozero import MCP3008
from time import sleep
import alsaaudio
import math

from pyaudio import PyAudio

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import show_message
from luma.core.legacy.font import proportional, LCD_FONT

import RPi.GPIO as GPIO

import sounddevice as sd

try:
    from itertools import izip
except ImportError: # Python 3
    izip = zip
    xrange = range

def sine_tone(frequency, duration, volume=1, sample_rate=22050):
    n_samples = int(sample_rate * duration)
    restframes = n_samples % sample_rate

    p = PyAudio()
    stream = p.open(format=p.get_format_from_width(1), # 8bit
                    channels=1, # mono
                    rate=sample_rate,
                    output=True)
    s = lambda t: volume * math.sin(2 * math.pi * frequency * t / sample_rate)
    samples = (int(s(t) * 0x7f + 0x80) for t in xrange(n_samples))
    for buf in izip(*[samples]*sample_rate): # write several samples at a time
        stream.write(bytes(bytearray(buf)))

    # fill remainder of frameset with silence
    stream.write(b'\x80' * restframes)

    stream.stop_stream()
    stream.close()
    p.terminate()


pot = MCP3008(0)
fsr = MCP3008(5)

m = alsaaudio.Mixer()
c_v = m.getvolume()
print(c_v)

p_c = 0

serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, cascaded=4, block_orientation=-90)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(25, GPIO.IN)

def readadc(adcnum):
    if adcnum > 7 or adcnum < 0:
        return -1
    r = spi_d.xfer2([1, 8 + adcnum << 4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    return data

device.clear()

while True:
    #if not GPIO.input(25):
    #    device.contrast(2*16)
    #    print('yes')
    #else:
    #    device.contrast(14*16)
    #    print('no')
    #print(pot.value)
    if fsr.value <= 0.125:
        frequency = 262
        frequency1 = 330
        block = [0, 0, 3, 7]
    elif fsr.value <= 0.25:
        frequency = 294
        frequency1 = 294
        block = [4, 0, 7, 7]
    elif fsr.value <= 0.375:
        frequency = 330
        frequency1 = 330
        block = [8, 0, 11, 7]
    elif fsr.value <= 0.5:
        frequency = 349
        frequency1 = 349
        block = [12, 0, 15, 7]
    elif fsr.value <= 0.625:
        frequency = 392
        frequency1 = 392
        block = [16, 0, 19, 7]
    elif fsr.value <= 0.75:
        frequency = 440
        frequency1 = 440
        block = [20, 0, 23, 7]
    elif fsr.value <= 0.875:
        frequency = 494
        frequency1 = 494
        block = [24, 0, 27, 7]
    else:
        frequency = 523
        block = [28, 0, 31, 7]
        
    if pot.value <= 0.125:
        m.setvolume(12)
        p_c = 1 * 16
    elif pot.value <= 0.25:
        m.setvolume(25)
        p_c = 3 * 16
    elif pot.value <= 0.375:
        m.setvolume(38)
        p_c = 5 * 16
    elif pot.value <= 0.5:
        m.setvolume(50)
        p_c = 7 * 16
    elif pot.value <= 0.625:
        m.setvolume(63)
        p_c = 9 * 16
    elif pot.value <= 0.75:
        m.setvolume(75)
        p_c = 11 * 16
    elif pot.value <= 0.875:
        m.setvolume(88)
        p_c = 13 * 16
    else:
        m.setvolume(100)
        p_c = 15 * 16
    fs = 44100
    seconds = 0.2
    #print(fsr.value)
    #print(pot.value)
    print(m.getvolume())

    t = np.linspace(0, seconds, seconds * fs, False)

    note = np.sin(frequency * t * 2 * np.pi)
    note1 = np.sin(frequency1 * t * 2 * np.pi)

    audio = note * (2**15 - 1) / np.max(np.abs(note))
    audio = audio.astype(np.int16)
    audio1 = note1 * (2**15 - 1) / np.max(np.abs(note))
    audio1 = audio1.astype(np.int16)

    stereo_data = np.column_stack([audio, audio1])
    
    if not GPIO.input(25):
        device.contrast(p_c)
        #play_obj = sa.play_buffer(audio, 1, 2, fs)
        with canvas(device) as draw:
            draw.rectangle(block, fill="red")
        sd.play(stereo_data, 44100)
        sd.wait()
        #play_obj.wait_done()
    else:
        device.contrast(0)
        with canvas(device) as draw:
            draw.rectangle(block, fill="red")
            
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
