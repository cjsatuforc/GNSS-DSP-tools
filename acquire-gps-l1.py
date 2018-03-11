#!/usr/bin/env python

import sys
import os
import numpy as np
import scipy.signal
import scipy.fftpack as fft

import gnsstools.gps.ca as ca
import gnsstools.nco as nco
import gnsstools.resample as resample

# internal resampling rate to make FFTs pow2
fsn = 4096000.0

#
# Acquisition search
#

def search_dop(x,prn,sums,min,max,inc):
  fs = fsn
  n = int(fsn*ca.code_period)                      # 1 ms coherent integration
  incr = float(ca.code_length)/n
  c = ca.code(prn,0,0,incr,n)                      # obtain samples of the C/A code
  c = fft.fft(c)
  m_metric,m_code,m_doppler = 0,0,0
  for doppler in np.arange(min,max,inc):           # doppler bins
    q = np.zeros(n)
    w = nco.nco(-doppler/fs,0,n)
    for block in range(sums):                      # number of incoherent sums
      b = x[(block*n):((block+1)*n)]
      b = b*w
      z = fft.fft(b)
      #for i in range(0,8):
      #  print '%2d %6.1f %6.1f' % (i, z.real[i], z.imag[i])
      r = fft.ifft(c*np.conj(z))
      q = q + np.absolute(r)
    idx = np.argmax(q)
    metric = q[idx]/np.mean(q)
    if metric > m_metric:
      m_metric = metric
      m_shift = idx
      m_code = ca.code_length*(float(idx)/n)
      m_doppler = doppler
  return prn,m_metric,m_shift,m_code,m_doppler

def search(x,prn,sums,fine):
  coarse = 50
  prn,m_metric,m_shift,m_code,m_doppler = search_dop(x,prn,sums,-5000,5000,coarse)
  #print 'prn %d coarse %d' % (prn, m_doppler)
  if fine:
    window = coarse
    prn,m_metric,m_shift,m_code,m_doppler = search_dop(x,prn,sums,m_doppler-window,m_doppler+window,1)
    #print 'prn %d fine %d' % (prn, m_doppler)
  return prn,m_metric,m_shift,m_code,m_doppler

#
# main program
#

filename = sys.argv[1]        # input data, raw file, i/q interleaved, 8 bit signed (two's complement)
fs = float(sys.argv[2])       # sampling rate, Hz
coffset = float(sys.argv[3])  # offset to L1 carrier, Hz (positive or negative)

sums = 80
ms = sums+5
format = 0
complex = 1
filter = 'FIR'
bw = 3000000
interp = 0
all_prns = False
fine = True

for i in range(4, len(sys.argv)):
  a = sys.argv[i]
  if a == 'sum1':
    sums = 1
    ms = 1
  elif a == 'sum8':
    sums = 8
    ms = sums+5
  elif a == 'sum16':
    sums = 16
    ms = sums+5
  elif a == 'cs8':
    format = 0
  elif a == 'cs82':
    format = 1
  elif a == 'rs8':
    format = 0
    complex = 0
    interp = 1
  elif a == 'rs81':
    format = 2
    complex = 0
    interp = 1
  elif a == 'interp':
    interp = 1
  elif a == 'SE4150L':
    # simulate internal filtering of SE4150L
    # 3rd order Butterworth, -3dB (0.5) 2.2 MHz, -8dB (0.16) 4 MHz, -23dB (0.005) 8 MHz
    bw = 2200000
    filter = '3rd-order Butterworth'
    print 'SE4150L simulation: bw=%.0f' % bw
  elif a == 'nofilter':
    filter = 'nofilter'
  elif a == 'all_prns':
    all_prns = True
  elif a == 'coarse':
    print 'coarse doppler search'
    fine = False
  else:
    print 'UNKNOWN arg %s' % a
    sys.exit()

# read first ms of file and resample to fsn

n = int(fs*ca.code_period*ms)
fp = open(filename,"rb")

if all_prns:
  prns = ca.g2_delay.keys()
else:
  print 'search, fs=%.0f ms=%d n=%d sums=%d' % (fs, ms, n, sums)
  #prns = list(range(1,33))+[133,135,138,140]
  prns = list(range(1,33))

samps = resample.resample(fp,fs,fsn,coffset,format,complex,interp,bw,filter)
x = resample.get_samples(samps,n)

print 'shift is modulo fsn %d samples over code period %dms' % (fsn*ca.code_period,int(ca.code_period*1000))
print 'code_offset is modulo code length %d' % (ca.code_length)

# iterate (in parallel) over PRNs of interest

def worker(p):
  x,prn = p
  return search(x,prn,sums,fine)

import multiprocessing as mp

#prns = list(range(1,3))
# if using a limited prn list:
#   don't forget to include a prn that won't be found to establish the noise floor
#   or set threshold = 0
print 'searching for PRNs '+ str(prns)
cpus = mp.cpu_count()
results = mp.Pool(cpus).map(worker, map(lambda prn: (x,prn),prns))

prn,metric,shift,code,doppler = map(list,zip(*results))
nfloor = list(metric)
nfloor.sort()
nfloor = nfloor[0]
threshold = 1.3
#threshold = 2.0
#threshold = 2.5
#threshold = 0

for i in range(len(metric)):
  met = metric[i]/nfloor
  if met > threshold:
    g = ''
    for j in range(int(met*5)):
      g = g +'*'
    print 'prn %3d doppler % 7.1f shift %6d code_offset %6.1f metric % 5.2f %s' % (prn[i],doppler[i],shift[i],code[i],met,g)
