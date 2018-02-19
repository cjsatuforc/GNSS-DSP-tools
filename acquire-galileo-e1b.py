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

def search(x,prn):
  fs = 8192000.0
  n = 32768                                        # 4 ms coherent integration
  incr = float(e1b.code_length)/n
  c = e1b.code(prn,0,0,incr,n)                     # obtain samples of the E1-B code
  boc = nco.boc11(0,0,incr,n)
  c = fft.fft(np.concatenate((c*boc,np.zeros(n))))
  m_metric,m_code,m_doppler = 0,0,0
  for doppler in np.arange(-4000,4000,50):         # doppler bins
    q = np.zeros(2*n)
    w = nco.nco(-doppler/fs,0,2*n)
    for block in range(20):                        # 20 incoherent sums
      b = x[(block*n):((block+2)*n)]
      b = b*w
      r = fft.ifft(c*np.conj(fft.fft(b)))
      q = q + np.absolute(r)
    idx = np.argmax(q)
    if q[idx]>m_metric:
      m_metric = q[idx]
      m_code = e1b.code_length*(float(idx)/n)
      m_doppler = doppler
  m_code = m_code%e1b.code_length
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

# read first 85 ms of file and resample to fsn

ms = 85
n = int(fs*0.001*ms)
fp = open(filename,"rb")
fsn = 8192000.0

if len(sys.argv) > 4:
  samps = resample.resample(fp,fs,fsn,coffset,type='SE4150L')
else:
  samps = resample.resample(fp,fs,fsn,coffset,bw=8000000)

x = resample.get_samples_complex(samps,n)

# iterate (in parallel) over PRNs of interest

def worker(p):
  x,prn = p
  return search(x,prn)

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
