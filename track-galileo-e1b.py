#!/usr/bin/env python

import sys
import numpy as np

import gnsstools.galileo.e1b as e1b
import gnsstools.nco as nco
import gnsstools.discriminator as discriminator
import gnsstools.resample as resample

class tracking_state:
  def __init__(self,fs,prn,code_p,code_f,code_i,carrier_p,carrier_f,carrier_i,mode):
    self.fs = fs
    self.prn = prn
    self.code_p = code_p
    self.code_f = code_f
    self.code_i = code_i
    self.carrier_p = carrier_p
    self.carrier_f = carrier_f
    self.carrier_i = carrier_i
    self.mode = mode
    self.prompt1 = 0 + 0*(1j)
    self.carrier_e1 = 0
    self.code_e1 = 0
    self.eml = 0
    print mode

# tracking loops

def track(x,s):
  n = len(x)
  fs = s.fs

  x = nco.mix(x,-s.carrier_f/fs, s.carrier_p)
  s.carrier_p = s.carrier_p - n*s.carrier_f/fs
  s.carrier_p = np.mod(s.carrier_p,1)

  # 1540.0 = 1575.42(E1) / 1.023(chip rate)
  cf = (s.code_f+s.carrier_f/1540.0)/fs

  p_early = e1b.correlate(x, s.prn, 0, s.code_p-0.2, cf, e1b.e1b_code(prn), e1b.boc11)
  p_prompt = e1b.correlate(x, s.prn, 0, s.code_p, cf, e1b.e1b_code(prn), e1b.boc11)
  p_late = e1b.correlate(x, s.prn, 0, s.code_p+0.2, cf, e1b.e1b_code(prn), e1b.boc11)

  if s.mode=='FLL_WIDE':
    fll_k = 2.0
    a = p_prompt
    b = s.prompt1
    e = discriminator.fll_atan(a,b)
    s.carrier_f = s.carrier_f + fll_k*e
    s.prompt1 = p_prompt
  elif s.mode=='FLL_NARROW':
    fll_k = 0.6
    a = p_prompt
    b = s.prompt1
    e = discriminator.fll_atan(a,b)
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
  s.prompt = np.absolute(p_prompt)
  s.late = np.absolute(p_late)
  if (s.late+s.early)==0:
    e = 0
  else:
    e = (s.late-s.early)/(s.late+s.early)
  s.eml = e
  e1 = s.code_e1
  s.code_f = s.code_f + dll_k1*e + dll_k2*(e-e1)
  s.code_e1 = e

  s.code_p = s.code_p + n*cf
  s.code_p = np.mod(s.code_p,e1b.code_length)

  return p_prompt,s

#
# main program
#

# parse command-line arguments
# example:
#   ./track-galileo-e1b.py /dev/stdin 68873142.857 -8662285.714 12 -350 1274.2

filename = sys.argv[1]             # input data, raw file, i/q interleaved, 8 bit signed (two's complement)
fs = float(sys.argv[2])            # sampling rate, Hz
coffset = float(sys.argv[3])       # offset to L1 carrier, Hz (positive or negative)
prn = int(sys.argv[4])             # PRN code
doppler = float(sys.argv[5])       # initial doppler estimate from acquisition
code_offset = float(sys.argv[6])   # initial code offset from acquisition

# by default don't resample, only filter
fsn = fs
format = 0
complex = 1
interp = 0
#bw = 2200000
print 'WARNING: 3 MHz filtering used'
bw = 3000000
type = 'nofilter'

for i in range(7, len(sys.argv)):
  a = sys.argv[i]
  if a == 'cs8':
    format = 0
  elif a == 'cs82':
    format = 1
  elif a == 'rs8':
    format = 0
    complex = 0
  elif a == 'rs831':
    format = 2
    complex = 0
  elif a == 'SE4150L':
    type = 'SE4150L'
    bw = 2200000
  elif a == 'FIR':
    type = 'FIR'
    bw = 4000000
  elif a == 'down':
    fsn = 64000000
    if type == 'nofilter':
      type = 'FIR'
      bw = 8000000
  elif a == 'up':
    fsn = 69984000
    if type == 'nofilter':
      type = 'FIR'
      bw = 8000000
  elif a == 'half':
    fsn = fs/2
    if type == 'nofilter':
      type = 'FIR'
      bw = 8000000
  elif a == 'quarter':
    fsn = fs/4
    if type == 'nofilter':
      type = 'FIR'
      bw = 8000000
  else:
    print 'UNKNOWN arg %s' % a
    sys.exit()

fp = open(filename,"rb")

samps = resample.resample(fp,fs,fsn,coffset,format,complex,interp,bw,type)

n = int(fs*0.004*((e1b.code_length-code_offset)/e1b.code_length))  # align with 4 ms code boundary
x = resample.get_samples(samps,n)
code_offset += n*250.0*e1b.code_length/fs

s = tracking_state(fs=fs, prn=prn,                    # initialize tracking state
  code_p=code_offset, code_f=e1b.chip_rate, code_i=0,
  carrier_p=0, carrier_f=doppler, carrier_i=0,
  mode='PLL')

block = 0
coffset_phase = 0.0
sync = []
vote = []

while True:
  if s.code_p<e1b.code_length/2:
    n = int(fs*0.004*(e1b.code_length-s.code_p)/e1b.code_length)
  else:
    n = int(fs*0.004*(2*e1b.code_length-s.code_p)/e1b.code_length)

  x = resample.get_samples(samps,n)
  if x is None:
    break

  for j in range(4):
    a,b = int(j*n/4),int((j+1)*n/4)
    #print 'j=%d a=%d b=%d n=%d' % (j,a,b,n)
    p_prompt,s = track(x[a:b],s)
    #vars = block, np.real(p_prompt), np.imag(p_prompt), s.carrier_f, s.code_f-e1b.chip_rate, (180/np.pi)*np.angle(p_prompt), s.eml, s.early, s.prompt, s.late, 'OK' if s.prompt >= s.early and s.prompt >= s.late else ''
    #print '%3d re=%8.1f im=%8.1f car=%8.1f cf=%6.3f a=%12.3f e=%7.3f %8.1f(E) %8.1f(P) %8.1f(L) %s' % vars

    # try looking for I/NAV sync pattern
    if j == 0:
      vsum = np.sum(vote)
      if vsum == 0 or vsum == 1:
        bit = 0
      else:
        if vsum == 4 or vsum == 3:
          bit = 1
        else:
          bit = 8
      print '%4d %4d vote %s =%d %s' % (block, block/4, str(vote), bit, '****' if vsum == 2 else ('----' if vsum == 1 or vsum == 3 else ''))
      vote = []
      sync.append(bit)
      if len(sync) > 10:
        sync.pop(0)
      vars = block, block/4, str(sync), s.carrier_f, s.carrier_f-doppler, s.code_f-e1b.chip_rate, s.eml, '' if s.prompt >= s.early and s.prompt >= s.late else (s.mode +' UNLOCKED')
      print '%4d %4d sync %s car=%8.1f(%+5.1f) cf=%7.3f e=%7.3f %s' % vars
      if sync == [0,1,0,1,1,0,0,0,0,0]:
        print 'SYNC %d (%d) ==========================================================================================================' % (block/4,block/4+250)
      if sync == [1,0,1,0,0,1,1,1,1,1]:
        print 'SYNC-INV %d (%d) ======================================================================================================' % (block/4,block/4+250)
    idat = np.real(p_prompt)
    ddat = idat
    #qdat = np.imag(p_prompt)
    #ddat = idat if abs(idat) > abs(qdat) else qdat
    vote.append(1 if ddat > 0 else 0)
    
    block = block + 1
#    if block/4 == 100:
#      print 'FLL_NARROW'
#      s.mode = 'FLL_NARROW'
#    if (block%100)==0:
#      sys.stderr.write("%d\n"%block)
#    if block==500:
#      s.mode = 'FLL_NARROW'
#    if block==1000:
#      s.mode = 'PLL'
