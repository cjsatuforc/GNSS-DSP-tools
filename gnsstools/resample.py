import numpy as np
import scipy.signal

import gnsstools.nco as nco
import gnsstools.io as io

# resample from fs to fsn

class resample:
  def __init__(self,fp,fs,fsn,coffset,bw=0,type='FIR'):
    self.fp = fp;
    self.fs = fs;
    self.fsn = fsn;
    self.coffset = coffset;
    self.coffset_phase = 0.0;
    self.type = type;
    self.d = 0;

    if type != 'FIR':
      # simulate internal filtering of SE4150L
      # 3rd order Butterworth, -3dB (0.5) 2.2 MHz, -8dB (0.16) 4 MHz, -23dB (0.005) 8 MHz
      bw = 2200000.0
      print 'SE4150L filtering simulation, bw=%.0f' % bw
      self.b,self.a = scipy.signal.butter(3,bw/2/(fs/2),btype='lowpass')
      #w, h = scipy.signal.freqz(self.b, self.a)
      #for i in range(len(w)):
      #  print '%7.3f MHz %10.6f' % ((fs * 0.5 / np.pi) * w[i] *2.0 /1e6, abs(h[i]))
    else:
      if bw == 0:
        return None
      print 'FIR filtering, bw=%.0f' % bw
      self.h = scipy.signal.firwin(161,bw/2/(fs/2),window='hanning')
    
    if fsn != fs:
      print 'resampling, fs=%f fsn=%f' % (fs,fsn)

def get_samples_complex(s,n):
  #print 'get_samples_complex n=%d fs=%f fsn=%f co=%f %s' % (n,s.fs,s.fsn,s.coffset,s.type)
  x = io.get_samples_complex(s.fp,n)
  if x.any() == None:
    return None
  
  if s.d == 0:
    print 'I %d %d %d %d' % (x.real[0],x.real[1],x.real[2],x.real[3])
    print 'Q %d %d %d %d' % (x.imag[0],x.imag[1],x.imag[2],x.imag[3])
    s.d = 1
  
  if s.coffset != 0:
    nco.mix(x,-s.coffset/s.fs,s.coffset_phase)
    s.coffset_phase = s.coffset_phase - n*s.coffset/s.fs
    s.coffset_phase = np.mod(s.coffset_phase,1)

  if s.type != 'FIR':
    x = scipy.signal.filtfilt(s.b,s.a,x)
  else:
    x = scipy.signal.filtfilt(s.h,[1],x)

  if s.fsn == s.fs:
    return x
  else:
    fsr = s.fs/s.fsn
    ms = int(n/s.fs*1e3)
    spms_n = int(s.fsn/1e3)
    xa = fsr*np.arange(ms*spms_n)
    xp = np.arange(len(x))
    #print 'Lxa=%d Lxp=%d Lx=%d' % (len(xa),len(xp),len(x))
    xr = np.interp(xa,xp,np.real(x))
    xi = np.interp(xa,xp,np.imag(x))
    return xr+(1j)*xi
