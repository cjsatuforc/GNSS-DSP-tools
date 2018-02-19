#!/usr/bin/env python

import sys
import os
import numpy as np
import scipy.signal
import scipy.fftpack as fft

import gnsstools.gps.ca as ca
import gnsstools.nco as nco
import gnsstools.io as io
import gnsstools.resample as resample

#
# Acquisition search
#

def search(x,prn):
  fs = 4096000.0
  n = 4096                                         # 1 ms coherent integration
  incr = float(ca.code_length)/n
  c = ca.code(prn,0,0,incr,n)                      # obtain samples of the C/A code
  c = fft.fft(c)
  m_metric,m_code,m_doppler = 0,0,0
  for doppler in np.arange(-5000,5000,200):        # doppler bins
    q = np.zeros(n)
    w = nco.nco(-doppler/fs,0,n)
    for block in range(80):                        # 80 incoherent sums
      b = x[(block*n):((block+1)*n)]
      b = b*w
      r = fft.ifft(c*np.conj(fft.fft(b)))
      q = q + np.absolute(r)
    idx = np.argmax(q)
    metric = q[idx]/np.mean(q)
    if metric>m_metric:
      m_metric = metric
      m_code = ca.code_length*(float(idx)/n)
      m_doppler = doppler
  return prn,m_metric,m_code,m_doppler

#
# main program
#

filename = sys.argv[1]        # input data, raw file, i/q interleaved, 8 bit signed (two's complement)
fs = float(sys.argv[2])       # sampling rate, Hz
coffset = float(sys.argv[3])  # offset to L1 carrier, Hz (positive or negative)

# read first 85 ms of file and resample to fsn

ms = 85
n = int(fs*0.001*ms)
fp = open(filename,"rb")
fsn = 4096000.0

if len(sys.argv) > 4:
  samps = resample.resample(fp,fs,fsn,coffset,type='SE4150L')
else:
  samps = resample.resample(fp,fs,fsn,coffset,bw=2200000)

x = resample.get_samples_complex(samps,n)

# iterate (in parallel) over PRNs of interest

def worker(p):
  x,prn = p
  return search(x,prn)

import multiprocessing as mp

prns = list(range(1,33))+[133,135,138,140]
print 'searching for PRNs '+ str(prns)
cpus = mp.cpu_count()
results = mp.Pool(cpus).map(worker, map(lambda prn: (x,prn),prns))

prn,metric,code,doppler = map(list,zip(*results))
nfloor = list(metric)
nfloor.sort()
nfloor = nfloor[0]
threshold = 2.0
#threshold = 2.5
#threshold = 0

for i in range(len(metric)):
  met = metric[i]/nfloor
  if met > threshold:
    print 'prn %3d doppler % 7.1f metric % 5.2f code_offset %6.1f' % (prn[i],doppler[i],met,code[i])
