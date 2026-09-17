import struct,re
import bmg
def entries(path):
    """일본판 BMG → {idx: (원문(태그 제거), 줄목록)}"""
    b=path if isinstance(path,(bytes,bytearray)) else open(path,'rb').read()
    E,enc,secs,ents,dat=bmg.parse(b)
    out={}
    for i,(off,_) in enumerate(ents):
        q=off; s=[]
        # 오프셋 0 은 빈 문자열 공유
        while True:
            c=dat[q]
            if c==0: break
            if c==0x1a:
                ln=dat[q+1]; tag=dat[q+2:q+ln]
                s.append(('TAG',tag)); q+=ln; continue
            if 0x81<=c<=0x9f or 0xe0<=c<=0xfc:
                s.append(dat[q:q+2].decode('cp932','replace')); q+=2
            else:
                s.append(chr(c)); q+=1
        # 후리가나 태그: ff00 02 NN + 읽기 → 본문은 태그 뒤에 그대로 있음
        text=''.join(x for x in s if isinstance(x,str))
        tags=[x[1].hex() for x in s if not isinstance(x,str)]
        if text.strip(): out[i]=(text,tags)
    return out
