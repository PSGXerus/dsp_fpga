#!/usr/bin/env python
# -*- coding: utf-8 -*-
#===========================================================================
# FIX_pyaudio_quantization.py
#
# Demonstration von Quantisierungseffekten auf Audiosignale:
#
# Eine Audio-Datei wird blockweise eingelesen, in numpy-Arrays umgewandelt 
# dann werden linker und rechter Kanal getauscht und die Datei wird auf
# ein Audio-Device ausgegeben.
#
# 
#===========================================================================
#from __future__ import division, print_function, unicode_literals # v3line15

import numpy as np
import numpy.random as rnd
from numpy import (pi, log10, exp, sqrt, sin, cos, tan, angle, arange,
                    linspace, array, zeros, ones)
from numpy.fft import fft, ifft, fftshift, ifftshift, fftfreq
import scipy.signal as sig
import scipy.interpolate as intp

import matplotlib.pyplot as plt
from matplotlib.pyplot import (figure, plot, stem, grid, xlabel, ylabel,
    subplot, title, clf, xlim, ylim)

import dsp_fpga_lib as dsp
import dsp_fpga_fix_lib as fx
#------------------------------------------------------------------ v3line30
# Ende der gemeinsamen Import-Anweisungen
import pyaudio
import wave
np_type = np.int16
wf = wave.open(r'C:\Windows\Media\chord.wav', 'rb') # open WAV-File in read mode
#wf = wave.open(r'D:\Musik\wav\Jazz\07 - Duet.wav')
#wf = wave.open(r'D:\Daten\share\Musi\wav\Feist - My Moon My Man.wav')
wf = wave.open(r'D:\Daten\share\Musi\wav\01 - Santogold - L.E.S Artistes.wav')
p = pyaudio.PyAudio() # instantiate PyAudio + setup PortAudio system

# open a stream on the desired device with the desired audio parameters 
# for reading or writing
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True) 
CHUNK = 1024 # number of samples in one frame

#q_obj = (14, 0, 'fix', 'sat') # try 'round' ; 'sat'
q_obj = {'Q':13.0,'quant':'fix','ovfl':'sat'}  # große Grenzzyklen bei QI = 0
fx_Q_l = fx.Fixed(q_obj)
fx_Q_r = fx.Fixed(q_obj) 


# initialize arrays for samples
samples_in = samples_out = zeros(CHUNK*2, dtype=np_type) # stereo
samples_l  = samples_r = zeros(CHUNK, dtype=np_type) # mono

data_out = 'dummy'


while data_out:

# read CHUNK frames to string, convert to numpy array and split in R / L chan.:
# R / L samples are interleaved, each sample is 16 bit = 2 Bytes
    samples_in = np.fromstring(wf.readframes(CHUNK), dtype=np_type)

## dtype = np.int8 (8 bits) = 1 ndarray element
##    two consecutive bytes / ndarray elements = 1 sample    
#    samples_l[0::2] = samples[0::4]
#    samples_l[1::2] = samples[1::4]
#    samples_r[0::2] = samples[2::4]
#    samples_r[1::2] = samples[3::4]
## Do some numpy magic here
#    samples_new[0::4] = samples_l[0::2]
#    samples_new[1::4] = samples_l[1::2]
#    samples_new[2::4] = samples_r[0::2]
#    samples_new[3::4] = samples_r[1::2]
#---------------------------------------------------------------------------
## dtype = np.int16 (16 bits): 1 ndarray element = 1 sample :
    samples_l = samples_in[0::2]
    samples_r = samples_in[1::2]
    if len(samples_r) < CHUNK: # check whether frame has full length
        samples_out = samples_np = zeros(len(samples_in), dtype=np_type)
        samples_l = samples_l = zeros(len(samples_in)/2, dtype=np_type)

# Quantize signals here:
    
#    samples_out[0::2] = fx_Q_l.fix(samples_l)
#    samples_out[1::2] = fx_Q_r.fix(samples_r)
    samples_out = fx_Q_r.fix(samples_in).astype(np_type)    
       
## Stereo signal processing: This only works for sample-by-sample operations,
## not e.g. for filtering where consecutive samples are combined
    
#    samples_out = abs(samples_in)
#    samples_out = ((samples_in.astype(np.float32))**2 /2**15).astype(np_type)
    samples_out = sqrt(samples_in.astype(np.float32)**2).astype(np_type)
    
#    data_out = np.chararray.tostring(samples_np.astype(np_type)) # convert back to string
    data_out = np.chararray.tostring(samples_out) # convert back to string
    stream.write(data_out) # play audio by writing audio data to the stream (blocking)
#    data_out = wf.readframes(CHUNK) # direct streaming without numpy

stream.stop_stream() # pause audio stream
stream.close() # close audio stream

p.terminate() # close PyAudio & terminate PortAudio system