import json,zipfile
z=zipfile.ZipFile('chal_WHZ50JK.zip')
spec=json.loads(z.read('cipher_spec.json')); s=spec['sbox']
pairs=json.loads(z.read('known_pairs.json'))
MASK=(1<<20)-1
def rot(x,n): return ((x<<n)|(x>>(20-n)))&MASK
def rkof(k,i,sch):
 if sch==0:return (k>>(5*i))&65535
 if sch==1:return (k>>(5*(3-i)))&65535
 if sch==2:return rot(k,5*i)&65535
 if sch==3:return rot(k,5*(3-i))&65535
 if sch==4:return (k+i*0x9e37)&65535
 return ((k+i*0x9e37)^(k>>(4*i)))&65535
def f(r,rk,mode):
 a=(r^(rk&255)) if mode&1 else ((r+(rk&255))&255)
 y=s[a]
 return (y^((rk>>8)&255)) if mode&2 else ((y+(rk>>8))&255)
def enc(x,k,sch,mode,swap):
 l=x>>8; r=x&255
 for i in range(4): l,r=r,l^f(r,rkof(k,i,sch),mode)
 return ((r<<8)|l) if swap else ((l<<8)|r)
def dec(x,k,sch,mode,swap):
 l=x>>8; r=x&255
 if swap:l,r=r,l
 for i in range(3,-1,-1): l,r=r^f(l,rkof(k,i,sch),mode),l
 return ((r<<8)|l) if swap else ((l<<8)|r)
for sch in range(6):
 for mode in range(4):
  for swap in range(2):
   mp={}; p,c=pairs[0]['plaintext'],pairs[0]['ciphertext']
   for k in range(1<<20): mp.setdefault(enc(p,k,sch,mode,swap),[]).append(k)
   hits=[]
   for k2 in range(1<<20):
    for k1 in mp.get(dec(c,k2,sch,mode,swap),[]):
     if all(enc(enc(q['plaintext'],k1,sch,mode,swap),k2,sch,mode,swap)==q['ciphertext'] for q in pairs):hits.append((k1,k2))
   if hits: print('HIT',sch,mode,swap,hits)
