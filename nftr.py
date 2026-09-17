import struct,sys
def parse(b):
    assert b[:4]==b'RTFN'
    r={}
    p=struct.unpack_from('<H',b,0xc)[0]
    fnif=b[p:]
    r['fnif']=fnif[8:0x1c].hex()
    r['height']=fnif[9]; r['enc']=fnif[0xf]
    pcglp,pcwdh,pcmap=struct.unpack_from('<III',fnif,0x10)
    r['cglp']=pcglp; 
    cg=b[pcglp-8:]
    tw,th,ts,base,mw,bpp=struct.unpack_from('<BBHbBB',cg,8)
    r.update(tw=tw,th=th,bpp=bpp,base=base,mw=mw)
    csize=struct.unpack_from('<I',cg,4)[0]
    r['nglyph']=(csize-0x10)//ts
    cmap={}; claimed=[]
    while pcmap and pcmap<len(b):
        c=b[pcmap-8:]
        lo,hi,typ,nxt=struct.unpack_from('<HHHxxI',c,8)
        tmp={}
        if typ==0:
            base0=struct.unpack_from('<H',c,0x14)[0]
            for i,ch in enumerate(range(lo,hi+1)): tmp[ch]=base0+i
        elif typ==1:
            for i,ch in enumerate(range(lo,hi+1)):
                g=struct.unpack_from('<H',c,0x14+2*i)[0]
                if g!=0xffff: tmp[ch]=g
        else:
            n=struct.unpack_from('<H',c,0x14)[0]
            for i in range(n):
                ch,g=struct.unpack_from('<HH',c,0x16+4*i); tmp[ch]=g
        for ch,g in tmp.items():
            if not any(a<=ch<=b2 for a,b2 in claimed): cmap[ch]=g
        claimed.append((lo,hi))
        pcmap=nxt
    r['cmap']=cmap
    return r
if __name__=='__main__':
    for f in sys.argv[1:]:
        r=parse(open(f,'rb').read()); cm=r.pop('cmap')
        ks=sorted(cm)
        print(f.split('/')[-1],r,'codes',len(cm), 'range',hex(ks[0]),hex(ks[-1]))
