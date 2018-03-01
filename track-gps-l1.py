#!/usr/bin/env python

import sys
import numpy as np

import gnsstools.gps.ca as ca
import gnsstools.nco as nco
import gnsstools.discriminator as discriminator
import gnsstools.resample as resample

class tracking_state:
  def __init__(self,fs,prn,code_p,code_f,code_i,carrier_p,carrier_f,carrier_i,chip_offset,mode):
    self.fs = fs
    self.prn = prn
    self.code_p = code_p
    self.code_f = code_f
    self.code_i = code_i
    self.carrier_p = carrier_p
    self.carrier_f = carrier_f
    self.carrier_i = carrier_i
    self.chip_offset = chip_offset
    self.mode = mode
    self.prompt1 = 0 + 0*(1j)
    self.carrier_e1 = 0
    self.code_e1 = 0
    self.eml = 0
    self.carrier_cyc = 0
    self.code_cyc = 0
    print 'loop filter', mode, 'chip_offset', chip_offset

# tracking loops

def track(x,s):
  n = len(x)
  fs = s.fs

  x = nco.mix(x,-s.carrier_f/fs, s.carrier_p)
  s.carrier_p = s.carrier_p - n*s.carrier_f/fs
  t = np.mod(s.carrier_p,1)
  dcyc = int(round(s.carrier_p-t))
  s.carrier_cyc += dcyc
  s.carrier_p = t

  # 1540.0 = 1575.42(L1) / 1.023(chip rate)
  cf = (s.code_f+s.carrier_f/1540.0)/fs

  p_early = ca.correlate(x, s.prn, 0, s.code_p-chip_offset, cf, ca.ca_code(prn))
  p_prompt = ca.correlate(x, s.prn, 0, s.code_p, cf, ca.ca_code(prn))
  p_late = ca.correlate(x, s.prn, 0, s.code_p+chip_offset, cf, ca.ca_code(prn))

  if s.mode=='FLL_WIDE':
    fll_k = 3.0
    a = p_prompt
    b = s.prompt1
    e = discriminator.fll_atan2(a,b)
    s.carrier_f = s.carrier_f + fll_k*e
    s.prompt1 = p_prompt
  elif s.mode=='FLL_NARROW':
    fll_k = 0.3
    a = p_prompt
    b = s.prompt1
    e = discriminator.fll_atan2(a,b)
    s.carrier_f = s.carrier_f + fll_k*e
    s.prompt1 = p_prompt
  elif s.mode=='PLL':
    pll_k1 = 0.1
    pll_k2 = 5.0
    e = discriminator.pll_costas(p_prompt)
    e1 = s.carrier_e1
    s.carrier_f = s.carrier_f + pll_k1*e + pll_k2*(e-e1)
    s.carrier_e1 = e

# code loop

  dll_k1 = 0.00002
  dll_k2 = 0.2
  s.early = np.absolute(p_early)
  s.early_n = s.early
  s.prompt = np.absolute(p_prompt)
  s.prompt_n = s.prompt
  s.late = np.absolute(p_late)
  s.late_n = s.late
  if (s.late+s.early)==0:
    e = 0
  else:
    e = (s.late-s.early)/(s.late+s.early)
  s.eml = e
  e1 = s.code_e1
  s.code_f = s.code_f + dll_k1*e + dll_k2*(e-e1)
  s.code_e1 = e

  s.code_p = s.code_p + n*cf
  t = np.mod(s.code_p,ca.code_length)
  dcyc = int(round(s.code_p-t))
  s.code_cyc += dcyc
  s.code_p = t

  return p_prompt,s

#
# main program
#

# parse command-line arguments
# example:
#   ./track-gps-l1.py data/gps-6002-l1_a.dat 68873142.857 -8662285.714 12 -400 781.2

filename = sys.argv[1]             # input data, raw file, i/q interleaved, 8 bit signed (two's complement)
fs = float(sys.argv[2])            # sampling rate, Hz
coffset = float(sys.argv[3])       # offset to L1 carrier, Hz (positive or negative)
prn = int(sys.argv[4])             # PRN code
doppler = float(sys.argv[5])       # initial doppler estimate from acquisition
code_offset = float(sys.argv[6])   # initial code offset from acquisition

# by default don't resample
fsn = fs
format = 0
complex = 1
chip_offset = 0.5
filter = 'nofilter'
bw = 2200000
interp = 0

for i in range(7, len(sys.argv)):
  a = sys.argv[i]
  if a == 'cs8':
    format = 0
  elif a == 'cs82':
    format = 1
  elif a == 'rs8':
    format = 0
    complex = 0
  elif a == 'rs81':
    format = 2
    complex = 0
  elif a == 'narrow_corr':
    chip_offset = 0.05
    print 'narrow_corr chip_offset', chip_offset
  else:
    print 'UNKNOWN arg %s' % a
    sys.exit()

fp = open(filename,"rb")

if fsn != fs:
  print 'resampler does not work for streaming yet'
  sys/exit()
samps = resample.resample(fp,fs,fsn,coffset,format,complex,interp,bw,filter)
fs = fsn

n = int(fs*0.001*((ca.code_length-code_offset)/ca.code_length))  # align with 1 ms code boundary
x = resample.get_samples(samps,n)
code_offset += n*1000.0*ca.code_length/fs

s = tracking_state(fs=fs, prn=prn,                    # initialize tracking state
  code_p=code_offset, code_f=ca.chip_rate, code_i=0,
  carrier_p=0, carrier_f=doppler, carrier_i=0, chip_offset=chip_offset,
  mode='PLL')

block = 0
coffset_phase = 0.0
samp = 0

while True:
  if s.code_p<ca.code_length/2:
    n = int(fs*0.001*(ca.code_length-s.code_p)/ca.code_length)
  else:
    n = int(fs*0.001*(2*ca.code_length-s.code_p)/ca.code_length)

  x = resample.get_samples(samps,n)
  samp += n

  p_prompt,s = track(x,s)

  #vars = block, np.real(p_prompt), np.imag(p_prompt), s.carrier_f, s.code_f-ca.chip_rate, (180/np.pi)*np.angle(p_prompt), s.early, s.prompt, s.late, s.code_cyc, s.code_p, s.carrier_cyc, s.carrier_p, samp, 'OK' if s.prompt >= s.early and s.prompt >= s.late else ''
  #print '%d %f %f %f %f %f %.0f(E) %.0f(P) %.0f(L) %d %f %d %f %d %s' % vars
  unlocked = False if s.prompt_n >= s.early_n and s.prompt_n >= s.late_n else True
  if unlocked:
    vars = block, s.carrier_f, s.eml, s.early_n, s.prompt_n, s.late_n, (s.mode +' UNLOCKED') if unlocked else ''
    print '%3d car=%6.1f e=%6.3f %7.0f(E) %7.0f(P) %7.0f(L) %s' % vars

  block = block + 1
  if (block%100)==0:
    sys.stderr.write("PRN%d %d\n" % (prn,block))
#  if block==500:
#    s.mode = 'FLL_NARROW'
#  if block==1000:
#    s.mode = 'PLL'
