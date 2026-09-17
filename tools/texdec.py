"""DS 텍스처(ntfq) 디코더/인코더 + 형식 추정"""
import struct
from PIL import Image
DIMS=[8,16,32,64,128,256,512]

def rgb555(v):
    r=v&31; g=v>>5&31; b=v>>10&31
    return (r*255//31, g*255//31, b*255//31)

def pal_of(b):
    return [rgb555(struct.unpack_from('<H',b,i)[0]) for i in range(0,len(b)-1,2)]

def data_len(fmt,w,h):
    return {'PLTT4':w*h//4,'PLTT16':w*h//2,'PLTT256':w*h,'A5I3':w*h,'A3I5':w*h,'COMP4x4':w*h//4+w*h//8}[fmt]

def decode(b,fmt,w,h):
    n=data_len(fmt,w,h); pb=b[n:]; pal=pal_of(pb)
    im=Image.new('RGBA',(w,h)); px=im.load()
    if fmt in('PLTT4','PLTT16','PLTT256'):
        bits={'PLTT4':2,'PLTT16':4,'PLTT256':8}[fmt]; mask=(1<<bits)-1
        for y in range(h):
            for x in range(w):
                i=y*w+x; v=(b[i*bits//8]>>((i*bits)%8))&mask
                c=pal[v] if v<len(pal) else (255,0,255)
                px[x,y]=c+((0,) if v==0 else (255,))
    elif fmt in('A5I3','A3I5'):
        ib=3 if fmt=='A5I3' else 5
        for y in range(h):
            for x in range(w):
                v=b[y*w+x]; I=v&((1<<ib)-1); A=v>>ib
                a=A*255//((1<<(8-ib))-1)
                if I<len(pal): c=pal[I]
                else: g=I*255//((1<<ib)-1); c=(g,g,g)
                px[x,y]=c+(a,)
    else:  # COMP4x4
        bw,bh=w//4,h//4; nb=bw*bh
        for by in range(bh):
            for bx in range(bw):
                k=by*bw+bx
                tex=struct.unpack_from('<I',b,k*4)[0]
                idx=struct.unpack_from('<H',b,nb*4+k*2)[0]
                mode=idx>>14; po=(idx&0x3fff)*2
                def P(j): return pal[po+j] if po+j<len(pal) else (255,0,255)
                c0,c1=P(0),P(1)
                if mode==0: cs=[c0,c1,P(2),None]
                elif mode==1: cs=[c0,c1,tuple((a+b2)//2 for a,b2 in zip(c0,c1)),None]
                elif mode==2: cs=[c0,c1,P(2),P(3)]
                else: cs=[c0,c1,tuple((5*a+3*b2)//8 for a,b2 in zip(c0,c1)),tuple((3*a+5*b2)//8 for a,b2 in zip(c0,c1))]
                for t in range(16):
                    v=tex>>(t*2)&3; c=cs[v]
                    px[bx*4+t%4,by*4+t//4]=(0,0,0,0) if c is None else c+(255,)
    return im

def candidates(b):
    L=len(b); out=[]
    for w in DIMS:
        for h in DIMS:
            if w*h<64: continue
            for fmt in ['COMP4x4','PLTT16','PLTT4','PLTT256','A5I3','A3I5']:
                if fmt=='COMP4x4' and (w<4 or h<4): continue
                n=data_len(fmt,w,h); p=L-n
                if p<0 or p%2: continue
                cols=p//2
                if fmt=='PLTT4' and not(1<=cols<=4): continue
                if fmt=='PLTT16' and not(1<=cols<=16): continue
                if fmt=='PLTT256' and not(17<=cols<=256): continue
                if fmt in('A5I3','A3I5'):
                    ib=3 if fmt=='A5I3' else 5
                    if not(1<=cols<=(1<<ib)): continue
                    if fmt=='A3I5' and cols<=8 and cols!=1: pass
                    mx=max(v&((1<<ib)-1) for v in b[:n])
                    if mx>=cols: continue
                if fmt=='PLTT256' and max(b[:n])>=cols: continue
                if fmt=='COMP4x4':
                    if cols<2: continue
                    nb=w*h//16; ok=True; used=0
                    for k in range(nb):
                        idx=struct.unpack_from('<H',b,n-nb*2+k*2)[0]
                        need=(idx&0x3fff)*2+(4 if (idx>>14)in(0,2) else 2)
                        used=max(used,need)
                    if used>cols or used<cols-8: continue
                out.append((fmt,w,h))
    return out
