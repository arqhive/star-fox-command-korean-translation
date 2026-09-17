import struct,sys
def parse(b):
    assert b[:8]==b'MESGbmg1'
    E='>' if b[8]==0 else '<'
    size,nsec=struct.unpack_from(E+'II',b,8)
    enc=b[0x10]
    p=0x20; secs={}
    for _ in range(nsec):
        mag=b[p:p+4]; sz=struct.unpack_from(E+'I',b,p+4)[0]
        secs[mag]=(p,sz); p+=sz
    ip,_=secs[b'INF1']; n,es=struct.unpack_from(E+'HH',b,ip+8)
    dp,_=secs[b'DAT1']
    ents=[]
    for i in range(n):
        e=b[ip+0x10+i*es:ip+0x10+(i+1)*es]
        off=struct.unpack_from(E+'I',e,0)[0]
        ents.append((off,e[4:]))
    return E,enc,secs,ents,b[dp+8:dp+secs[b'DAT1'][1]]
def decode(b,E,enc,off):
    out=[];p=off
    if enc==2 or enc==3 or enc==1 and False: pass
    while p<len(b):
        if enc in(2,):
            c=struct.unpack_from(E+'H',b,p)[0]; p+=2
            if c==0: break
            if c==0x1a:
                ln=b[p+(0 if E=='<' else 0)]
                # tag: 1a len ...
                ln=b[p]; tag=b[p-2+2:p-2+ln*1]
                raw=b[p-2:p-2+ln]; out.append('{'+raw[2:].hex()+'}'); p=p-2+ln; continue
            out.append(chr(c) if c>=0x20 else '\n' if c==10 else '<%02x>'%c)
        else:
            c=b[p]
            if c==0: break
            if c==0x1a:
                ln=b[p+1]; out.append('{'+b[p+2:p+ln].hex()+'}'); p+=ln; continue
            if enc==3 or enc==1:  # sjis 2byte?
                if (0x81<=c<=0x9f or 0xe0<=c<=0xfc):
                    out.append(b[p:p+2].decode('cp932','replace')); p+=2; continue
            out.append(chr(c) if c>=0x20 else '\n' if c==10 else '<%02x>'%c); p+=1
    return ''.join(out)
if __name__=='__main__':
    b=open(sys.argv[1],'rb').read()
    E,enc,secs,ents,dat=parse(b)
    print('endian',E,'enc',enc,'secs',{k:v for k,v in secs.items()},'n',len(ents),'entsize',len(ents[0][1])+4)
    lim=int(sys.argv[2]) if len(sys.argv)>2 else 99999
    for i,(off,attr) in enumerate(ents[:lim]):
        print(i,attr.hex(),decode(dat,E,enc,off))
