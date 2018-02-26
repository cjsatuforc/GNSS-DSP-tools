import sys
import math
import numpy as np
import scipy.signal as sig

import gnsstools.nco as nco
import gnsstools.io as io

# resample from fs to fsn

class resample:
  def __init__(self,fp,fs,fsn,coffset,format,complex,interp,bw,filter):
    self.fp = fp
    self.fs = fs
    self.fsn = fsn
    self.coffset = coffset
    self.coffset_phase = 0.0
    self.format = format
    self.complex = complex
    self.interp = interp
    self.filter = filter
    self.bw = bw
    self.d = 0
    self.resample_up_down = False

    if filter == '3rd-order Butterworth':
      print 'filter: 3rd-order Butterworth: bw=%.0f' % bw
      self.b,self.a = sig.butter(3,bw/2/(fs/2),btype='lowpass')
      #w, h = sig.freqz(self.b, self.a)
      #for i in range(len(w)):
      #  print '%7.3f MHz %10.6f' % ((fs * 0.5 / np.pi) * w[i] *2.0 /1e6, abs(h[i]))
    elif filter == 'FIR':
      if bw == 0:
        return None
      print 'filter: FIR bw=%.0f' % bw
      self.h = sig.firwin(161,bw/2/(fs/2),window='hanning')
    elif filter == 'nofilter':
      print 'filter: nofilter'
    else:
      print 'filter: %s?' % filter
      sys.exit()
    
    if filter != 'nofilter' and interp == 0 and fsn != fs:
      target_rem = 0.0001
      approx_rem = 1
      found_up = 0
      found_down = 0
      found_exact = False
      for up in range(1, 102401):
        down = (fs * up) / fsn
        down_rem = abs(down - math.floor(down))
        if down_rem == 0:
          found_exact = True
          found_up = up;
          found_down = down;
          break
        else:
          if down_rem <= target_rem:
            if down_rem < approx_rem:
              approx_rem = down_rem;
              found_up = up;
              found_down = down;
      found_approx = True if found_exact is False and approx_rem != 1 else False
      match = 'exact' if found_exact else ('approx' if found_approx else 'NOT_FOUND')
      print 'resampling: %s=%.6f fs=%.0f up=%d fsn=%.0f down=%d' % (match, down_rem if found_approx else 0, fs, up, fsn, down)
      #self.resample_up_down = True if found_exact or found_approx else False
      self.resample_up_down = True if found_exact else False
      self.up = found_up
      self.down = found_down
    
    if format == 0:
      print 'format: complex signed 8-bit'
    elif format == 1:
      print 'format: complex sign-bit only saturated to +127/-127'
    elif format == 2:
      print 'format: SPECIAL real sign-bit only mode'

def get_samples(s,n):
  #print 'get_samples n=%d fs=%f fsn=%f co=%f %s' % (n,s.fs,s.fsn,s.coffset,s.filter)
  if s.complex == 1:
    x = io.get_samples_complex(s.fp,n)
  else:
    x = io.get_samples_real(s.fp,n)
  
#  if s.d == 0:
#    xc = np.copy(x)

  # sign bit, slightly reduced sensitivity
  if s.format == 1:
    print 'format 1'
    sat_max = 127
    sat_min = -127
    for i in range(len(x)):
      x.real[i] = sat_max if x.real[i] >= 0 else sat_min
      x.imag[i] = sat_max if x.imag[i] >= 0 else sat_min
  elif s.format == 2:
    # force to 1-bit
    print 'format 2'
    print 'x.dtype=', x.dtype
    for i in range(len(x)):
      x[i] = 1 if x[i] >= 0 else -1

#  if s.d == 0:
#    print 'I %d|%d %d|%d %d|%d %d|%d' % (xc.real[0],x.real[0],xc.real[1],x.real[1],xc.real[2],x.real[2],xc.real[3],x.real[3])
#    print 'Q %d|%d %d|%d %d|%d %d|%d' % (xc.imag[0],x.imag[0],xc.imag[1],x.imag[1],xc.imag[2],x.imag[2],xc.imag[3],x.imag[3])
#    s.d = 1
  
#  if s.format == 2:
#    for i in range(0,32):
#      print '%2d x %s' % (i, '+' if x[i] > 0 else '-')
#  else:
#    for i in range(0,32):
#      print '%2d x %s %s' % (i, '+' if x.real[i] > 0 else '-', '+' if x.imag[i] > 0 else '-')

  if s.coffset != 0:
    #print 'mix %.0f' % s.coffset
    x = nco.mix(x,-s.coffset/s.fs,s.coffset_phase)
    s.coffset_phase = s.coffset_phase - n*s.coffset/s.fs
    s.coffset_phase = np.mod(s.coffset_phase,1)
  
#  if s.format == 2:
#    # force to 1-bit
#    for i in range(len(x)):
#      x.real[i] = 1 if x.real[i] >= 0 else -1
#      x.imag[i] = 1 if x.imag[i] >= 0 else -1

  if s.filter == '3rd-order Butterworth':
    x = sig.filtfilt(s.b,s.a,x)
  elif s.filter == 'FIR':
    x = sig.filtfilt(s.h,[1],x)

  # cases where no resampling needed
  if s.filter == 'nofilter' or s.fsn == s.fs:
    return x
  else:
    if s.resample_up_down:
      xr = sig.resample_poly(np.real(x), s.up, s.down)
      xi = sig.resample_poly(np.imag(x), s.up, s.down)
      print 'resample_poly: fs=%.0f fsn=%.0f Lx=%d Lxr=%d up=%d down=%d' % (s.fs, s.fsn, len(x), len(xr), s.up, s.down)
    elif s.interp == 1:
      fsr = s.fs/s.fsn
      xa = fsr*np.arange(round(n*s.fsn/s.fs))
      xp = np.arange(len(x))
      print 'resample_interp: fs=%.0f fsn=%.0f n=%d Lxa=%d Lxp=%d Lx=%d' % (s.fs, s.fsn, n, len(xa), len(xp), len(x))
      xr = np.interp(xa,xp,np.real(x))
      xi = np.interp(xa,xp,np.imag(x))
    
    return xr+(1j)*xi
