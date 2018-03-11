# Galileo E1-B code construction
#
# Copyright 2014 Peter Monta

import numpy as np

from e1b_strings import *

chip_rate = 1023000
code_length = 4092
code_period = float(code_length) / chip_rate

def e1b_parse_hex(prn):
  s = e1b_strings[prn]
  n = code_length
  y = np.zeros(n)
  for i in range(n):
    nib = i//4
    bit = 3-(i%4)
    y[i] = (int(s[nib],16)>>bit)&1
  return y

codes = {}

def e1b_code(prn):
  if prn not in codes:
    codes[prn] = e1b_parse_hex(prn)
  return codes[prn]

boc11 = np.array([1.0,-1.0])
boc11b = [1,0,0]
code_vec = []

def code(prn,chips,frac,incr,n):
  c = e1b_code(prn)
  idx = (chips%code_length) + frac + incr*np.arange(n)
  fc = np.floor(idx).astype('int')
  fc = np.mod(fc,code_length)
  hc = np.floor(idx*2).astype('int')
  hc = np.mod(hc,2)

  bp = (2*(chips+frac)%2) + 2*incr*np.arange(n)
  bp = np.mod(bp,2)
  bp = np.floor(bp).astype('int')

  x = c[fc]
  x = (1.0 - 2.0*x)  # binary to *inverted* bipolar
  x2 = x * boc11[bp]
  
  # boc11[-1,1]: -1.0 => invert, 1.0 => no change
  # boc11b[0,1]:    0 => invert,   1 => no change

  x3 = np.zeros(len(x))
  for i in range(len(x)):
    if hc[i] != bp[i]:
      print '%d fc %d hc %d bp %d' % (i, fc[i], hc[i], bp[i])
    # important: shows that phase bit half_chip comes from is equivalent to boc11b[1,0]
    #x3[i] = int(c[fc[i]]) ^ boc11b[bp[i]]
    #x3[i] = int(c[fc[i]]) ^ hc[i]
    x3[i] = int(c[fc[i]]) ^ (0 if hc[i] else 1)   # polarity of boc11b doesn't matter
  x3 = (1.0 - 2.0*x3)  # binary to inverted bipolar

  if False:
    for i in range(32*8*2):
      print 'i %4d fc %2d hc %d c %.0f %.1f | boc11 %.1f c2 %.1f | boc11b %d c3 %.1f' % (i,fc[i],hc[i],c[fc[i]],x[i], boc11[bp[i]],x2[i], boc11b[bp[i]],x3[i])
  if False:
    for i in range(len(x)):
      if fc[i] == boc11b[2]:
        boc11b[2] = boc11b[2]+1
        if boc11b[2] == 32:
          boc11b[2] = -1
        code_vec.append(int(c[fc[i]]))
        print code_vec

  return x3

try:
  from numba import jit
except:
  def jit(**kwargs):
    return lambda x: x

#@jit(nopython=True)
# e1b.correlate_boc11(x, s.prn, 0, s.code_p-s.chip_offset, cf, e1b.e1b_code(prn), e1b.boc11)
def correlate_boc11(x,prn,chips,frac,incr,c,boc11):
  n = len(x)
  p = 0.0j
  cp = (chips+frac)%code_length
  bp = (2*(chips+frac))%2
  for i in range(n):
    boc = boc11[int(bp)]
    #if i < 24:
    #  print 'i %5d bp %.1f boc[%d] %.1f cp %d code %.1f' % (i,bp,int(bp),boc,int(cp),c[int(cp)])
    p += x[i]*(1.0-2.0*c[int(cp)]) * boc
    cp = (cp+incr)%code_length
    bp = (bp+2*incr)%2
  return p

# e1b.correlate_slow_boc11(x, s.prn, 0, s.code_p-s.chip_offset, cf, e1b.e1b_code(prn), e1b.boc11)
def correlate_slow_boc11(x,prn,chips,frac,incr,c,boc11):
  n = len(x)
  q = code(prn,chips,frac,incr,n)
  return np.sum(x*q)

@jit(nopython=True)
def correlate(x,prn,chips,frac,incr,c,boc11):
  n = len(x)
  p = 0.0j
  cp = (chips+frac)%code_length
  bp = (2*(chips+frac))%2
  bp6 = (12*(chips+frac))%2
  for i in range(n):
    cboc = 0.953463*boc11[int(bp)] + 0.301511*boc11[int(bp6)]
    p += x[i]*(1.0-2.0*c[int(cp)])*cboc
    cp = (cp+incr)%code_length
    bp = (bp+2*incr)%2
    bp6 = (bp6+12*incr)%2
  return p

# test

if __name__=='__main__':
  # f5d71
  print(e1b_code(1)[0:20])
  # 96b85
  print(e1b_code(2)[0:20])
