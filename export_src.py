import json,re,os
import romfiles, paths
os.chdir(paths.HERE)
os.makedirs('trans/src', exist_ok=True)
from ko_metrics import FontInfo, FONTMAP
from jpload import entries
LIMIT={'advertise':248,'battle':188,'enemy':115,'scenario':196,'strategy':190}
def load_en(f):
    """북미판 롬이 있으면 같은 인덱스의 영어 문장을 참고로 붙인다"""
    try:
        return {i:t for i,(t,_) in entries(romfiles.read(f'2D/MessageText/{f}_En.bmg', paths.US_ROM)).items()}
    except Exception:
        return {}
CHUNKS={'scenario':4,'battle':2,'strategy':2}
allsrc={}
for f,fonts in FONTMAP.items():
    fi=FontInfo(romfiles.read(f'2D/MessageText/{fonts[0]}.nftr'))
    en=load_en(f)
    items=[]
    for i,(t,_) in sorted(entries(romfiles.read(f'2D/MessageText/{f}.bmg')).items()):
        if not re.search(r'[ぁ-んァ-ヶ一-龯]',t): continue   # 일본어 없는 항목(％, 디버그 번호)은 제외
        jpw=max(fi.width(l,ko=False) for l in t.split('\n'))
        items.append({'id':i,'jp':t,'en':en.get(i,'').strip(),'lines':t.count('\n')+1,'max_px':max(LIMIT[f],jpw)})
    allsrc[f]=items
    print(f,len(items))
chunks={}
for f in ['scenario','battle','strategy']:
    n=CHUNKS[f]; k=(len(allsrc[f])+n-1)//n
    for j in range(n): chunks[f'{f}_{j+1}']=allsrc[f][j*k:(j+1)*k]
chunks['advertise_enemy']=[dict(x,file='advertise') for x in allsrc['advertise']]+[dict(x,file='enemy') for x in allsrc['enemy']]
for name,items in chunks.items():
    for x in items: x.setdefault('file',name.split('_')[0])
    json.dump(items,open(f'trans/src/{name}.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
    print(name,len(items),items[0]['id'],'-',items[-1]['id'])
