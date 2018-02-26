import numpy as np

NT = 1024
nco_table = np.exp(2*(np.pi)*(1j)*np.arange(NT)*(1.0/NT))

def nco(f,p,n):
  idx = p + f*np.arange(n)
  idx = np.floor(idx*NT).astype('int')
  idx = np.mod(idx,NT)
  return nco_table[idx]

def boc11(chips,frac,incr,n):
  c = np.array([-1,1])
  boc11_length = 2
  idx = (chips%boc11_length) + frac + incr*np.arange(n)
  idx = idx*2
  idx = np.floor(idx).astype('int')
  idx = np.mod(idx,boc11_length)
  return c[idx]

try:
  import numba
  from numba import jit
except:
  def jit(**kwargs):
    return lambda x: x
  class numba:
    int64 = None

@jit(nopython=True,locals={'dp': numba.int64, 'df': numba.int64})
def mix_complex(x,f,p,tab):
  n = len(x)
  dp = int(np.floor(p*NT*(1<<50)))
  df = int(np.floor(f*NT*(1<<50)))
  for i in range(n):
    idx = dp>>50
    x[i] *= tab[idx&(NT-1)]
    dp += df
  return x

@jit(nopython=True,locals={'dp': numba.int64, 'df': numba.int64})
def mix_real(z,x,f,p,tab):
  n = len(x)
  dp = int(np.floor(p*NT*(1<<50)))
  df = int(np.floor(f*NT*(1<<50)))
  for i in range(n):
    idx = dp>>50
    z.real[i] = x[i] * tab.real[idx&(NT-1)]
    z.imag[i] = x[i] * tab.imag[idx&(NT-1)]
    dp += df
  return z

def mix(x,f,p):
  #print 'mix >>>>', x.dtype, nco_table.dtype
  if str(x.dtype).startswith('complex'):
    return mix_complex(x,f,p,nco_table)
  else:
    z = np.zeros(len(x),dtype='c8')
    return mix_real(z,x,f,p,nco_table)
