def lz10_dec(d):
    assert d[0]==0x10, hex(d[0])
    size=d[1]|d[2]<<8|d[3]<<16; p=4; o=bytearray()
    while len(o)<size:
        fl=d[p]; p+=1
        for i in range(8):
            if len(o)>=size: break
            if fl&(0x80>>i):
                b1,b2=d[p],d[p+1]; p+=2
                n=(b1>>4)+3; disp=((b1&0xf)<<8|b2)+1
                for _ in range(n): o.append(o[-disp])
            else:
                o.append(d[p]); p+=1
    return bytes(o)
def lz10_comp(d):
    # simple greedy compressor
    o=bytearray([0x10,len(d)&0xff,len(d)>>8&0xff,len(d)>>16&0xff]); i=0
    from collections import defaultdict
    while i<len(d):
        flagpos=len(o); o.append(0); fl=0
        for b in range(8):
            if i>=len(d): break
            best=0;bd=0
            start=max(0,i-4096)
            j=d.rfind(d[i:i+3],start,i+2) if i+3<=len(d) else -1
            while j>=start and j<i:
                l=0
                while l<18 and i+l<len(d) and d[j+l]==d[i+l]: l+=1
                if l>best: best=l;bd=i-j
                if best==18: break
                j=d.rfind(d[i:i+3],start,j+2) if j>start else -1
            if best>=3:
                fl|=0x80>>b; o+=bytes([((best-3)<<4)|((bd-1)>>8),(bd-1)&0xff]); i+=best
            else:
                o.append(d[i]); i+=1
        o[flagpos]=fl
    while len(o)%4: o.append(0)
    return bytes(o)
