"""이미지 한글화 작업 도구 (작업 폴더: tools)
python imgtool.py info <경로>    : 형식/크기/팔레트 출력 + img/work/<경로>_grid.png (확대+8px 격자, 노란선 32px)
                                  + 북미판 참고 이미지 img/work/<경로>_us.png (있으면)
python imgtool.py render <경로>  : img/spec/<경로>.json 적용 → 게임 형식으로 인코드 → 다시 디코드한 결과를
                                  img/work/<경로>_preview.png 로 저장 (위: 원본, 아래: 결과)
경로 예) 3D 텍스처: Menu/General/menu_txt   (3D/Textures/ 와 .ntfq-cmp 생략)
         2D 그림:   2D/Pause/pause_wnd       (확장자 생략)
spec 형식은 texlib.py 상단 설명 참고.
"""
import sys, os, json
import numpy as np
from PIL import Image, ImageDraw
import texlib, bg2d
from texdec import decode, pal_of, data_len, candidates
from ndsfs import parse
from lz import lz10_dec

_us = None
def us_rom():
    global _us
    if _us is None:
        import paths
        _us = parse(paths.US_ROM)
    return _us

BGCH = None
def load_any(rel):
    """rel → (kind, image, ctx)"""
    global BGCH
    if rel.startswith('2D/'):
        if BGCH is None: BGCH = json.load(open(os.path.join(texlib.ROOT, 'bgchoice.json')))
        c, s, p, keys = bg2d.load(texlib.rom(), rel)
        tw = BGCH[rel]
        return '2d', bg2d.decode(c, s, p, tw), (c, s, p, tw, keys)
    path = '3D/Textures/' + rel + '.ntfq-cmp'
    fmt, w, h, raw = texlib.tex_info(path)
    return '3d', decode(raw, fmt, w, h), (fmt, w, h, raw, path)

def encode_any(kind, ctx, img):
    """→ {rom경로: 비압축 bytes}"""
    if kind == '3d':
        fmt, w, h, raw, path = ctx
        return {path: texlib.encode(fmt, w, h, raw, img)}
    c, s, p, tw, (kc, ks, kp) = ctx
    c2, s2 = bg2d.encode(c, s, p, tw, img)
    out = {kc: c2}
    if ks: out[ks] = s2
    return out

def decode_back(kind, ctx, enc):
    if kind == '3d':
        fmt, w, h, raw, path = ctx
        return decode(enc[path], fmt, w, h)
    c, s, p, tw, (kc, ks, kp) = ctx
    return bg2d.decode(enc[kc], enc.get(ks) if ks else None, p, tw)

def us_image(kind, rel, ctx):
    import paths
    if not os.path.exists(paths.US_ROM):
        return None  # 북미판 롬이 없으면 참고 이미지 생략
    d, h, files = us_rom()
    try:
        if kind == '2d':
            base = rel + '_En'
            c, s, p, keys = bg2d.load(us_rom(), base)
            if c is None: return None
            n = (len(s) // 2) if s is not None else len(c) // 32
            return bg2d.decode(c, s, p, ctx[3])
        fmt, w, hh, raw, path = ctx
        up = path.replace('.ntfq-cmp', '_En.ntfq-cmp')
        if up not in files: return None
        fid, s_, e_ = files[up]; b = lz10_dec(d[s_:e_])
        for f, ww, hh2 in candidates(b):
            if (ww, hh2) == (w, hh): return decode(b, f, ww, hh2)
    except Exception as ex:
        print('북미판 참고 이미지 실패:', ex)
    return None

def main():
    cmd, rel = sys.argv[1], sys.argv[2].replace('\\', '/')
    rel = rel.replace('3D/Textures/', '').replace('.ntfq-cmp', '')
    kind, img, ctx = load_any(rel)
    os.makedirs(os.path.dirname('img/work/' + rel), exist_ok=True)
    w, h = img.size
    if cmd == 'info':
        if kind == '3d':
            fmt, _, _, raw, _ = ctx; pal = pal_of(raw[data_len(fmt, w, h):])
            print('형식', fmt, '크기', w, 'x', h, '팔레트 색 수', len(pal))
            if fmt != 'COMP4x4': print('팔레트', ['#%02x%02x%02x' % c for c in pal])
        else:
            print('형식 2D-BG(16색 타일)', '크기', w, 'x', h, '팔레트', ['#%02x%02x%02x' % c for c in bg2d.palette(ctx[2])], '(0번=투명)')
        S = 4 if w <= 256 else 2
        base = Image.new('RGBA', img.size, (60, 70, 90, 255)); base.alpha_composite(img)
        g = base.resize((w * S, h * S), Image.NEAREST); dr = ImageDraw.Draw(g)
        for x in range(0, w, 8): dr.line([(x * S, 0), (x * S, h * S)], fill=(255, 255, 0) if x % 32 == 0 else (200, 0, 0))
        for y in range(0, h, 8): dr.line([(0, y * S), (w * S, y * S)], fill=(255, 255, 0) if y % 32 == 0 else (200, 0, 0))
        for x in range(0, w, 32): dr.text((x * S + 2, 2), str(x), fill=(255, 255, 0))
        for y in range(32, h, 32): dr.text((2, y * S + 2), str(y), fill=(255, 255, 0))
        out = 'img/work/' + rel + '_grid.png'; g.convert('RGB').save(out)
        print('격자 이미지:', out, f'({S}배 확대, 노란선 32px, 빨간선 8px)')
        u = us_image(kind, rel, ctx)
        if u is not None:
            ub = Image.new('RGBA', u.size, (60, 70, 90, 255)); ub.alpha_composite(u.convert('RGBA'))
            ub.resize((u.width * 2, u.height * 2), Image.NEAREST).convert('RGB').save('img/work/' + rel + '_us.png')
            print('북미판 참고:', 'img/work/' + rel + '_us.png', '(2배)')
    elif cmd == 'render':
        spec = json.load(open('img/spec/' + rel + '.json', encoding='utf-8'))
        new = texlib.apply(img, spec)
        enc = encode_any(kind, ctx, new)
        back = decode_back(kind, ctx, enc)
        out = 'img/work/' + rel + '_preview.png'
        texlib.preview(img, back, out, scale=2 if w > 128 else 3)
        print('미리보기:', out)

if __name__ == '__main__':
    main()
