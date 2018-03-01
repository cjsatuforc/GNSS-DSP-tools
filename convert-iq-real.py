#!/usr/bin/env python

import sys
import os
import math as math
import numpy as np

import gnsstools.io as io

fn_in = sys.argv[1]        # input data, raw file, i/q interleaved, 8 bit signed (two's complement)
fn_out = sys.argv[2]        # output data, raw file, real only, 8 bit signed (two's complement)
fs = float(sys.argv[3])       # sampling rate, Hz
coffset = float(sys.argv[4])  # offset to L1 carrier, Hz (positive or negative)

ms = 200

for i in range(5, len(sys.argv)):
  a = sys.argv[i]
  if a == 'xxx':
    foo = 0
  else:
    print 'UNKNOWN arg %s' % a
    sys.exit()

n = int(fs*0.001*ms)
fpi = open(fn_in,"rb")
fpo = open(fn_out,"wb")

x = io.get_samples_complex(fpi, n)
y = []
for i in range(n):
  z = round(math.sqrt(x.real[i]*x.real[i] + x.imag[i]*x.imag[i]))
  print 'z', z, i, x.real[i], x.imag[i]
  if z > 255 or z < -256:
    sys.exit()
  y.append(z)
#io.put_samples_real(fpo, y, n)
