"""사용법: python check_ko.py <청크이름>   예) python check_ko.py scenario_1
work/src/<청크>.json 원문과 translation/ko/<청크>.json 번역을 대조해 문제를 출력한다."""
import json,sys,re,os
import romfiles, paths
os.chdir(paths.ROOT)
from ko_metrics import FontInfo, FONTMAP
name=sys.argv[1]
src=json.load(open(f'work/src/{name}.json',encoding='utf-8'))
try: ko=json.load(open(f'translation/ko/{name}.json',encoding='utf-8'))
except FileNotFoundError: print('번역 파일 없음'); sys.exit(1)
fonts={}
errs=0
def err(i,msg):
    global errs; errs+=1; print(f'[{i}] {msg}')
keys=set()
for x in src:
    f=x['file']; key=f"{f}:{x['id']}" if name=='advertise_enemy' else str(x['id'])
    keys.add(key)
    if f not in fonts: fonts[f]=FontInfo(romfiles.read(f'2D/MessageText/{FONTMAP[f][0]}.nftr'))
    t=ko.get(key)
    if t is None or not t.strip(): err(key,'번역 누락'); continue
    lines=t.split('\n')
    if len(lines)>x['lines']: err(key,f"줄 수 초과 {len(lines)} > {x['lines']}: {t!r}")
    for l in lines:
        w=fonts[f].width(l)
        if w>x['max_px']: err(key,f"폭 초과 {w}px > {x['max_px']}px: {l!r}")
        if l!=l.strip(): err(key,f"줄 앞뒤 공백: {l!r}")
    if x['jp'].count('@1')!=t.count('@1'): err(key,'@1 치환기호 개수 불일치')
    if re.search(r'[ぁ-んァ-ヶ一-龯]',t): err(key,f'일본어 문자 남음: {t!r}')
    for ch in t:
        if ch=='\n': continue
        try: ch.encode('cp949')
        except UnicodeEncodeError:
            try: ch.encode('cp932')
            except UnicodeEncodeError: err(key,f'표시 불가 문자 {ch!r}')
for k in ko:
    if k not in keys: err(k,'원문에 없는 키')
print(f'{name}: 원문 {len(src)}개, 번역 {len(ko)}개, 문제 {errs}개')
sys.exit(1 if errs else 0)
