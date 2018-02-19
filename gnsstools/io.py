import numpy as np

def get_samples_complex(fp,n):
  #print 'io.get_samples_complex n=%d' % n
  z = fp.read(2*n)
  if len(z)!=2*n:
    return None
  s = np.fromstring(z,dtype='int8')
  #print 'len=%d %d %d %d %d' % (len(s),s[0],s[1],s[2],s[3])
  #for i in range(len(s)):
  #  s[i] = 1 if s[i] > 0 else 0
  s.shape = (n,2)
  x = np.empty(n,dtype='c8')
  x.real = s[:,0]
  x.imag = s[:,1]
  return x
