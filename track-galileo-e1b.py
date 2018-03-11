#!/usr/bin/env python

import sys
import numpy as np

import gnsstools.galileo.e1b as e1b
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
    self.sync = []
    self.ntotal = 0.0
    print 'loop filter', mode, 'chip_offset', chip_offset

# tracking loops

def track(x,s):
  n = len(x)
  fs = s.fs

  # LO mix (doppler only, carrier has already been removed)
  x = nco.mix(x,-s.carrier_f/fs, s.carrier_p)
  s.carrier_p = s.carrier_p - n*s.carrier_f/fs
  s.carrier_p = np.mod(s.carrier_p,1)

  # 1540.0 = 1575.42(E1) / 1.023(chip rate)
  cf = (s.code_f+s.carrier_f/1540.0)/fs

  # correlate_boc11(x,prn,chips,frac,incr,c,boc11)
  #p_early = e1b.correlate_boc11(x, s.prn, 0, s.code_p-s.chip_offset, cf, e1b.e1b_code(prn), e1b.boc11)
  #p_prompt = e1b.correlate_boc11(x, s.prn, 0, s.code_p, cf, e1b.e1b_code(prn), e1b.boc11)
  #p_late = e1b.correlate_boc11(x, s.prn, 0, s.code_p+s.chip_offset, cf, e1b.e1b_code(prn), e1b.boc11)
  p_early = e1b.correlate_slow_boc11(x, s.prn, 0, s.code_p-s.chip_offset, cf, e1b.e1b_code(prn), e1b.boc11)
  p_prompt = e1b.correlate_slow_boc11(x, s.prn, 0, s.code_p, cf, e1b.e1b_code(prn), e1b.boc11)
  p_late = e1b.correlate_slow_boc11(x, s.prn, 0, s.code_p+s.chip_offset, cf, e1b.e1b_code(prn), e1b.boc11)

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

def locked(s,bit,symbol):
  s.sync.append(bit)
  if len(s.sync) > 10:
    s.sync.pop(0)
  unlocked = False if s.prompt >= s.early and s.prompt >= s.late else True
  if unlocked:
  #if True:
    vars = prn, symbol, str(s.sync), s.carrier_f, s.carrier_f-doppler, s.code_f-e1b.chip_rate, s.eml, (s.mode +' UNLOCKED') if unlocked else ''
    print 'PRN%d %4d sync %s car=%8.1f(%+5.1f) cf=%7.3f e=%7.3f %s' % vars
  if s.sync == [0,1,0,1,1,0,0,0,0,0]:
    print 'PRN%d SYNC-N %d (%d) %.0f ===============================================================' % (prn,symbol,symbol+250,s.ntotal)
    s.ntotal = 0;
  if s.sync == [1,0,1,0,0,1,1,1,1,1]:
    print 'PRN%d SYNC-I %d (%d) %.0f ===========================================================' % (prn,symbol,symbol+250,s.ntotal)
    s.ntotal = 0;
  return s


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

# by default don't resample
fsn = fs
format = 0
complex = 1
# original
#chip_offset = 0.2
# works
chip_offset = 0.25
# for 1/4 or 1/1 track rate eventually goes unlocked on some samples, but still gets sync!
#chip_offset = 0.5
filter = 'nofilter'
bw = 8000000
interp = 0
oversample_4x = True

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
  elif a == 'SE4150L':
    # simulate internal filtering of SE4150L
    # 3rd order Butterworth, -3dB (0.5) 2.2 MHz, -8dB (0.16) 4 MHz, -23dB (0.005) 8 MHz
    bw = 2200000
    filter = '3rd-order Butterworth'
    print 'SE4150L simulation: bw=%.0f' % bw
  elif a == 'FIR':
    filter = 'FIR'
    bw = 4000000
  elif a == 'down':
    fsn = 64000000
    if filter == 'nofilter':
      filter = 'FIR'
      bw = 8000000
  elif a == 'up':
    fsn = 69984000
    if filter == 'nofilter':
      filter = 'FIR'
      bw = 8000000
  elif a == 'half':
    fsn = fs/2
    if filter == 'nofilter':
      filter = 'FIR'
      bw = 8000000
  elif a == 'quarter':
    fsn = fs/4
    if filter == 'nofilter':
      filter = 'FIR'
      bw = 8000000
  elif a == 'interp':
    interp = 1
  elif a == '1x':
    oversample_4x = False
  else:
    print 'UNKNOWN arg %s' % a
    sys.exit()

print '%s' % ('oversample 4x' if oversample_4x else 'sample 1x')

fp = open(filename,"rb")

if fsn != fs:
  print 'resampler does not work for streaming yet'
  sys/exit()
state = resample.resample(fp,fs,fsn,coffset,format,complex,interp,bw,filter)
fs = fsn

n = int(fs*0.004*((e1b.code_length-code_offset)/e1b.code_length))  # align with 4 ms code boundary
x = resample.get_samples(state,n)
print 'code alignment n', n
code_offset += n*250.0*e1b.code_length/fs

s = tracking_state(fs=fs, prn=prn,                    # initialize tracking state
  code_p=code_offset, code_f=e1b.chip_rate, code_i=0,
  carrier_p=0, carrier_f=doppler, carrier_i=0, chip_offset=chip_offset,
  mode='PLL')

symbol = 0
coffset_phase = 0.0
vote = []
spchip = fs/e1b.chip_rate
print 'spchip', spchip

while True:
  if s.code_p < e1b.code_length/2:
    n = int(fs*0.004*(e1b.code_length-s.code_p)/e1b.code_length)
  else:
    n = int(fs*0.004*(2*e1b.code_length-s.code_p)/e1b.code_length)
  #print 'n', n

  x = resample.get_samples(state,n)
  s.ntotal += float(n)

  if oversample_4x:
    for j in range(4):
      a,b = int(j*n/4),int((j+1)*n/4)
      #print 'j=%d a=%d b=%d n=%d' % (j,a,b,n)
      p_prompt,s = track(x[a:b],s)
      #vars = symbol, np.real(p_prompt), np.imag(p_prompt), s.carrier_f, s.code_f-e1b.chip_rate, (180/np.pi)*np.angle(p_prompt), s.eml, s.early, s.prompt, s.late, 'OK' if s.prompt >= s.early and s.prompt >= s.late else ''
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
        #if vsum != 0 and vsum != 4:
        #  print '%4d %4d vote %s =%d %s' % (symbol, symbol/4, str(vote), bit, '****' if vsum == 2 else ('----' if vsum == 1 or vsum == 3 else ''))
        vote = []
        s = locked(s,bit,symbol/4)
      #} j0
      
      vote.append(1 if np.real(p_prompt) > 0 else 0)
    
      symbol = symbol + 1
    #} j0..3

  else:
    p_prompt,s = track(x,s)
    bit = 1 if np.real(p_prompt) > 0 else 0
    s = locked(s,bit,symbol)
    symbol = symbol + 1

#} while T

#    if symbol/4 == 100:
#      print 'FLL_NARROW'
#      s.mode = 'FLL_NARROW'
#    if (symbol%100)==0:
#      sys.stderr.write("%d\n"%symbol)
#    if symbol==500:
#      s.mode = 'FLL_NARROW'
#    if symbol==1000:
#      s.mode = 'PLL'
