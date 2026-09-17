import sys,os
from ndsfs import parse
from lz import lz10_dec
rom,out,pat=sys.argv[1],sys.argv[2],sys.argv[3]
d,h,files=parse(rom)
for k,(fid,s,e) in files.items():
    if pat in k:
        b=d[s:e]; name=k
        if k.endswith('-cmp') and e>s and b[0]==0x10:
            try: b=lz10_dec(b); name=k[:-4]
            except Exception as ex: print('fail',k,ex)
        p=os.path.join(out,name); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'wb').write(b)
