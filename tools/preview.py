import struct,sys
from PIL import Image
from ndsfs import parse
from lz import lz10_dec
import nftr, bmg
rom,h,files=parse(sys.argv[1])
def get(p):
    fid,s,e=files[p]; return lz10_dec(rom[s:e])
def render(fontname,bmgname,ids,out):
    fb=get('2D/MessageText/'+fontname+'.nftr-cmp'); r=nftr.parse(fb); cm=r['cmap']
    p=struct.unpack_from('<I',fb,0x10+0x10)[0]; cg=p-8
    tw,th,ts=fb[cg+8],fb[cg+9],struct.unpack_from('<H',fb,cg+10)[0]
    cwp=struct.unpack_from('<I',fb,0x10+0x14)[0]-8
    E,enc,secs,ents,dat=bmg.parse(get('2D/MessageText/'+bmgname+'.bmg-cmp'))
    imgs=[];maxw=0
    for i in ids:
        off=ents[i][0]; q=off; lines=[[]]
        while dat[q]:
            c=dat[q]
            if c==0x1a: q+=dat[q+1]; continue
            if c==0x0a: lines.append([]); q+=1; continue
            if c>=0x81 and c<=0x9f or c>=0xe0: code=c<<8|dat[q+1]; q+=2
            else: code=c; q+=1
            lines[-1].append(code)
        im=Image.new('L',(260,len(lines)*21+4),40)
        for ln,codes in enumerate(lines):
            x=2
            for code in codes:
                g=cm.get(code)
                if g is None: print('MISSING',hex(code)); continue
                left,gw,adv=struct.unpack_from('<bBB',fb,cwp+0x10+3*g)
                go=cg+0x10+g*ts
                for y in range(th):
                    for xx in range(tw):
                        bit=y*tw+xx
                        if fb[go+bit//8]>>(7-bit%8)&1 and x+left+xx<260: im.putpixel((x+left+xx,2+ln*21+y),255)
                x+=left+gw
            maxw=max(maxw,x-2)
        imgs.append(im)
    H=sum(i.height+4 for i in imgs); o=Image.new('L',(260,H),0); y=0
    for i in imgs: o.paste(i,(0,y)); y+=i.height+4
    o.resize((520,H*2),0).save(out); print(out,'max line px',maxw)
render(sys.argv[2],sys.argv[3],[int(x) for x in sys.argv[4].split(',')],sys.argv[5])
