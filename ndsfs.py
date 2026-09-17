import struct, sys, os
def parse(path):
    d = open(path,'rb').read()
    h = {}
    h['title']=d[0:12].decode('ascii','replace'); h['code']=d[12:16].decode(); h['maker']=d[16:18].decode()
    (h['arm9_off'],h['arm9_entry'],h['arm9_addr'],h['arm9_size'],
     h['arm7_off'],h['arm7_entry'],h['arm7_addr'],h['arm7_size'],
     h['fnt_off'],h['fnt_size'],h['fat_off'],h['fat_size'],
     h['ov9_off'],h['ov9_size'],h['ov7_off'],h['ov7_size']) = struct.unpack_from('<16I', d, 0x20)
    h['romsize']=struct.unpack_from('<I',d,0x80)[0]
    fnt=d[h['fnt_off']:h['fnt_off']+h['fnt_size']]
    fat=d[h['fat_off']:h['fat_off']+h['fat_size']]
    files={}
    def walk(dirid, prefix):
        off, first, _ = struct.unpack_from('<IHH', fnt, (dirid&0xfff)*8)
        fid=first
        while True:
            t=fnt[off]; off+=1
            if t==0: break
            n=t&0x7f; name=fnt[off:off+n].decode('ascii','replace'); off+=n
            if t&0x80:
                sub=struct.unpack_from('<H',fnt,off)[0]; off+=2
                walk(sub, prefix+name+'/')
            else:
                s,e=struct.unpack_from('<II',fat,fid*8)
                files[prefix+name]=(fid,s,e); fid+=1
    walk(0xf000,'')
    return d,h,files
if __name__=='__main__':
    d,h,files=parse(sys.argv[1])
    print({k:(hex(v) if isinstance(v,int) else v) for k,v in h.items()})
    print('files',len(files),'overlays',h['ov9_size']//32)
    for k,(fid,s,e) in sorted(files.items()):
        print(f'{fid:4d} {e-s:9d} {k}  {d[s:s+4]!r}')
