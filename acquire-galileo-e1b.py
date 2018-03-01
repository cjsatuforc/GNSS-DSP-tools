#!/usr/bin/env python

import sys
import os
import numpy as np
import scipy.signal
import scipy.fftpack as fft

import gnsstools.galileo.e1b as e1b
import gnsstools.nco as nco
import gnsstools.resample as resample

#
# Acquisition search
#

def search_dop(x,prn,sums,min,max,inc):
  fs = 8192000.0
  n = 32768                                        # 4 ms coherent integration
  incr = float(e1b.code_length)/n
  c = e1b.code(prn,0,0,incr,n)                     # obtain samples of the E1-B code
  boc = nco.boc11(0,0,incr,n)
  c = fft.fft(np.concatenate((c*boc,np.zeros(n))))
  m_metric,m_code,m_doppler = 0,0,0
  for doppler in np.arange(min,max,inc):           # doppler bins
    q = np.zeros(2*n)
    w = nco.nco(-doppler/fs,0,2*n)
    for block in range(sums):                      # number of incoherent sums
      b = x[(block*n):((block+2)*n)]
      #print 'blk=%d sums=%d Lx=%d Lb=%d Tw= Lw=%d' % (block, sums, len(x), len(b), len(w))
      b = b*w
      r = fft.ifft(c*np.conj(fft.fft(b)))
      q = q + np.absolute(r)
    idx = np.argmax(q)
    if q[idx] > m_metric:
      m_metric = q[idx]
      m_code = e1b.code_length*(float(idx)/n)
      m_doppler = doppler
  m_code = m_code%e1b.code_length
  return prn,m_metric,m_code,m_doppler

def search(x,prn,sums):
  coarse = 50
  prn,m_metric,m_code,m_doppler = search_dop(x,prn,sums,-4000,4000,coarse)
  #print 'prn %d coarse %d' % (prn, m_doppler)
  window = coarse
  prn,m_metric,m_code,m_doppler = search_dop(x,prn,sums,m_doppler-window,m_doppler+window,1)
  #print 'prn %d fine %d' % (prn, m_doppler)
  return prn,m_metric,m_code,m_doppler

#
# main program
#

# parse command-line arguments
# example:
#   ./acquire-galileo-e1b.py data/gps-5001-l1_a.dat 68873142.857 -8662285.714

filename = sys.argv[1]        # input data, raw file, i/q interleaved, 8 bit signed (two's complement)
fs = float(sys.argv[2])       # sampling rate, Hz
coffset = float(sys.argv[3])  # offset to E1 Galileo carrier, Hz (positive or negative)

sums = 20
ms = sums*4 + 5
search_2 = False
format = 0
complex = 1
filter = 'FIR'
bw = 3000000
interp = 0

for i in range(4, len(sys.argv)):
  a = sys.argv[i]
  if a == 'sum1':
    sums = 1
    ms = 1
  elif a == 'search2':
    search_2 = True
    ms = 8
    filter = 'nofilter'
  elif a == 'sum8':
    sums = 8
    ms = sums*4 + 5
  elif a == 'sum16':
    sums = 16
    ms = sum*4 + 5
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
  else:
    print 'UNKNOWN arg %s' % a
    sys.exit()

# read first ms of file and resample to fsn

n = int(fs*0.001*ms)
fp = open(filename,"rb")
fsn = 8192000.0

samps = resample.resample(fp,fs,fsn,coffset,format,complex,interp,bw,filter)
x = resample.get_samples(samps,n)

# iterate (in parallel) over PRNs of interest

def worker(p):
  x,prn = p
  return search(x,prn,sums)

import multiprocessing as mp

prns = list(range(1,51))
# if using a limited prn list:
#   don't forget to include a prn that won't be found to establish the noise floor
#   or set threshold = 0
#prns = [1,19,30]
print 'searching for PRNs '+ str(prns)
cpus = mp.cpu_count()
results = mp.Pool(cpus).map(worker, map(lambda prn: (x,prn),prns))

prn,metric,code,doppler = map(list,zip(*results))
#prn,metric,code,doppler = search(x,1,sums)

nfloor = list(metric)
nfloor.sort()
nfloor = nfloor[0]
threshold = 1.3
#threshold = 2.0
threshold = 2.0
#threshold = 2.5
#threshold = 0

for i in range(len(metric)):
  met = metric[i]/nfloor
  if met > threshold:
    g = ''
    for j in range(int(met*5)):
      g = g +'*'
    print 'prn %3d doppler % 7.1f code_offset %6.1f metric % 5.2f %s' % (prn[i],doppler[i],code[i],met,g)
