import csv

rows=[]
with open('extracted/attachments/parade_capture.csv') as f:
    for r in csv.DictReader(f):
        rows.append((int(r['time_ns']), [int(r[f'D{i}']) for i in range(8)]))

def transitions(ch):
    return [(t, v[ch]) for t,v in rows if len(transitions.seen)==0 or v[ch]!=transitions.seen[-1][1]]

def uart(ch=6):
    # transition-time UART decode, sample center of each bit after falling start edge
    out=[]
    prev=rows[0][1][ch]
    for idx,(t,v) in enumerate(rows[1:],1):
        x=v[ch]
        if prev==1 and x==0:
            bits=[]
            for k in range(10):
                ts=t+(k+0.5)*1e9/115200
                j=idx
                while j+1<len(rows) and rows[j+1][0] <= ts: j+=1
                bits.append(rows[j][1][ch])
            if bits[0]==0 and bits[9]==1:
                b=sum(bits[k+1]<<k for k in range(8))
                out.append((t,b))
        prev=x
    return out

def spi():
    out=[]; prev_sck=rows[0][1][2]; cur=[]
    for t,v in rows[1:]:
        cs, sck, mosi, miso = v[5],v[2],v[3],v[4]
        if cs==0 and prev_sck==0 and sck==1:
            cur.append((mosi,miso))
        if cs==1 and cur:
            out.append(cur); cur=[]
        prev_sck=sck
    if cur: out.append(cur)
    return out

def i2c():
    # Decode bytes by SDA value on each SCL rising edge, delimited by start/stop.
    out=[]; active=False; bits=[]; prev=rows[0][1]; tx=[]
    for t,v in rows[1:]:
        scl,sda= v[0],v[1]
        pscl,psda=prev[0],prev[1]
        if psda==1 and sda==0 and scl==1:
            if active and (bits or tx): out.append(tx)
            active=True; bits=[]; tx=[]
        if active and pscl==0 and scl==1:
            bits.append(sda)
            if len(bits)==9:
                tx.append(sum(bits[k]<<(7-k) for k in range(8)))
                tx.append('ACK' if bits[8]==0 else 'NACK')
                bits=[]
        if psda==0 and sda==1 and scl==1:
            if active: out.append(tx)
            active=False; bits=[]; tx=[]
        prev=v
    if active and (bits or tx): out.append(tx)
    return out

u=uart()
print('UART', len(u), bytes(x[1] for x in u))
print('UART hex', bytes(x[1] for x in u).hex())
print('SPI transactions', len(spi()))
for n, tr in enumerate(spi()):
    print('SPI',n,'len',len(tr),'mosi',bytes(sum(x[0]<<k for k in range(8)) for x in []))
    mb=[]; ib=[]
    for i in range(0,len(tr)-7,8):
        m=sum(tr[i+k][0]<<(7-k) for k in range(8)); q=sum(tr[i+k][1]<<(7-k) for k in range(8)); mb.append(m);ib.append(q)
    print(' ',bytes(mb),bytes(ib),bytes(mb).hex(),bytes(ib).hex())
print('I2C transactions',len(i2c()))
for x in i2c(): print('I2C',x)
