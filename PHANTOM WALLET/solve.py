import json, hmac, hashlib, subprocess, urllib.request
BASE='https://phantom-wallet.ip-167-235-30-42.swiftwave.xyz/api/v1'; APP='com.phantom.wallet'; DEV='and-0123456789abcdef0123'
def req(path, method='GET', headers=None, body=None):
 r=urllib.request.Request(BASE+path,method=method,headers=headers or {},data=body)
 try:
  with urllib.request.urlopen(r) as x:return json.loads(x.read())
 except urllib.error.HTTPError as e:
  print(e.code,e.read()); raise
def dec(k,stage,nonce,hx):
 key=hmac.new(k,('stage:'+stage+':').encode()+bytes.fromhex(nonce),hashlib.sha256).digest(); out=bytearray(); i=0; n=len(bytes.fromhex(hx))
 while len(out)<n:out+=hmac.new(key,i.to_bytes(4,'big'),hashlib.sha256).digest();i+=1
 return bytes(a^b for a,b in zip(bytes.fromhex(hx),out)).decode()
ch=req('/challenge',headers={'X-Phantom-App':APP,'X-Phantom-Device':DEV})
mat=subprocess.check_output(['java','-Djava.library.path=build','-cp','build','Harness','31bae05e58a1662a54d31444d4ee5117540644b14fb151f1414f30c55f4f72bb',ch['challenge']],env={'LD_LIBRARY_PATH':'build'}).decode().splitlines()[-1].split()[-1]; k=bytes.fromhex(mat)
epoch=ch['epoch']; msg=('POST\n/api/v1/session/register\n'+ch['challenge']+'\n'+str(epoch)+'\n'+DEV).encode(); token=hmac.new(k,msg,hashlib.sha256).hexdigest()
r=req('/session/register','POST',{'X-Phantom-App':APP,'X-Phantom-Device':DEV,'X-Phantom-Challenge':ch['challenge'],'X-Phantom-Epoch':str(epoch),'X-Phantom-Token':token})
sid,nonce,c=r['session_id'],r['session_nonce'],r['next_counter']
def api(path,method='GET',body=None):
 global c
 h={'X-Phantom-App':APP,'X-Phantom-Device':DEV,'X-Phantom-Session':sid,'X-Phantom-Counter':str(c),'X-Phantom-Sig':hmac.new(k,(method+'\n/api/v1'+path+'\n'+nonce+'\n'+str(c)).encode(),hashlib.sha256).hexdigest()}; c+=1
 if body is not None:h['Content-Type']='application/json; charset=utf-8'
 return req(path,method,h,json.dumps(body).encode() if body else None)
z=hmac.new(k,('totp:'+str(epoch//30)).encode(),hashlib.sha256).digest(); off=z[-1]&15; otp=str((int.from_bytes(z[off:off+4],'big')&0x7fffffff)%1000000).zfill(6)
a=api('/wallet/balance'); fa=dec(k,'wallet-balance',nonce,a['fragment']); t=api('/wallet/transactions'); fb=dec(k,'wallet-transactions',nonce,t['fragment']); v=api('/security/verify-2fa','POST',{'otp':otp}); fc=dec(k,'security-2fa',nonce,v['fragment'])
proof=hmac.new(k,(fa+fb+fc).encode(),hashlib.sha256).hexdigest(); print(api('/recovery/unlock','POST',{'proof':proof}))
