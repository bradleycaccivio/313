#!/usr/bin/python

import spidev
import time

import soundcard as sc
import numpy as np

print(sc.all_speakers())
print(sc.default_speaker().channels)

_d = np.array([100, 100])

sc.default_speaker().play(_d, 261, 1)