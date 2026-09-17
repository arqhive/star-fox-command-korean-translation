"""텍스처 로드/인코드 + 이미지 편집 명세(spec) 적용 라이브러리

spec JSON 형식 (translation/images/<텍스처 경로>.json):
{
  "edits": [
    {"op": "clear", "rect": [x, y, w, h]},                       # 투명으로 지움
    {"op": "fill",  "rect": [x, y, w, h], "color": "#rrggbb"},   # 단색 채움
    {"op": "copy",  "src": [x, y, w, h], "dst": [x, y]},         # 원본 이미지의 영역 복사(배경 복원용)
    {"op": "hfill", "rect": [x, y, w, h], "from_x": x0},         # 각 행을 x0 열의 픽셀로 채움(가로 그라데이션 배경 복원)
    {"op": "text",  "text": "싱글 플레이", "rect": [x, y, w, h],
       "font": "malgunbd" | "malgun" | "gulim" | "batang",
       "size": 12, "color": "#ffffff", "color2": "#aaaaaa"(선택: 세로 그라데이션 아래색),
       "outline": "#000000"(선택), "outline_w": 1, "shadow": [dx, dy, "#000000"](선택),
       "align": "left|center|right", "valign": "top|middle|bottom",
       "aa": true(안티앨리어싱), "line_gap": 0, "spacing": 0}
  ]
}
텍스트가 rect 폭보다 넓으면 자동으로 가로 압축된다. 여러 줄은 \n.
"""
import json, struct, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from texdec import decode, data_len, pal_of
from ndsfs import parse
from lz import lz10_dec

import paths
TOOLS = paths.TOOLS
ROOT = paths.ROOT
FONTS = {
    'malgunbd': 'C:/Windows/Fonts/malgunbd.ttf',
    'malgun': 'C:/Windows/Fonts/malgun.ttf',
    'gulim': 'C:/Windows/Fonts/gulim.ttc',
    'batang': 'C:/Windows/Fonts/batang.ttc',
}
_rom = None
def rom():
    global _rom
    if _rom is None:
        _rom = parse(paths.JP_ROM)
    return _rom

_choice = None
def tex_info(path):
    """path: '3D/Textures/...ntfq-cmp' → (fmt, w, h, raw)"""
    global _choice
    if _choice is None:
        _choice = json.load(open(os.path.join(TOOLS, 'texchoice.json')))
    d, h, files = rom()
    fid, s, e = files[path]
    raw = lz10_dec(d[s:e])
    fmt, w, hh = _choice[path]
    return fmt, w, hh, raw

def hexc(c):
    c = c.lstrip('#'); return tuple(int(c[i:i+2], 16) for i in (0, 2, 4))

# ---------------- 인코더 ----------------
def to555(c):
    return (c[0] * 31 + 127) // 255 | ((c[1] * 31 + 127) // 255) << 5 | ((c[2] * 31 + 127) // 255) << 10

def nearest(pal, c, start=0):
    arr = np.array(pal[start:], dtype=int)
    return start + int(((arr - np.array(c[:3])) ** 2).sum(1).argmin())

PAL_GROW_TOL = None  # None: COMP4x4 팔레트를 절대 늘리지 않음(기존 색 묶음만 사용)

def encode(fmt, w, h, raw, img):
    img = img.convert('RGBA')
    a = np.asarray(img).astype(int)
    n = data_len(fmt, w, h)
    if fmt in ('PLTT4', 'PLTT16', 'PLTT256'):
        pal = pal_of(raw[n:]); bits = {'PLTT4': 2, 'PLTT16': 4, 'PLTT256': 8}[fmt]
        out = bytearray(raw[:n]); cache = {}
        for y in range(h):
            for x in range(w):
                p = tuple(a[y, x])
                if p[3] < 128: v = 0
                else:
                    key = p[:3]
                    if key not in cache: cache[key] = nearest(pal, key, 1 if len(pal) > 1 else 0)
                    v = cache[key]
                i = y * w + x; bp = i * bits
                out[bp // 8] = (out[bp // 8] & ~(((1 << bits) - 1) << (bp % 8))) | (v << (bp % 8))
        return bytes(out) + raw[n:]
    if fmt in ('A5I3', 'A3I5'):
        ib = 3 if fmt == 'A5I3' else 5
        pal = pal_of(raw[n:]) or [(255, 255, 255)]
        out = bytearray(raw[:n]); cache = {}
        for y in range(h):
            for x in range(w):
                r, g, b, al = a[y, x]
                A = round(al / 255 * ((1 << (8 - ib)) - 1))
                if A == 0: I = 0
                else:
                    key = (r, g, b)
                    if key not in cache: cache[key] = nearest(pal, key)
                    I = cache[key]
                out[y * w + x] = (A << ib) | I
        return bytes(out) + raw[n:]
    # COMP4x4: 바뀐 블록만 재인코딩. 팔레트가 크게 늘면 게임의 팔레트 메모리가 넘쳐
    # 다른 텍스처 색이 깨지므로, 기존 팔레트의 색 묶음을 최대한 재사용한다.
    orig = np.asarray(decode(raw, fmt, w, h)).astype(int)
    bw, bh = w // 4, h // 4; nb = bw * bh
    tex = bytearray(raw[:nb * 4]); idx = bytearray(raw[nb * 4:nb * 6])
    palb = bytearray(raw[n:])
    P = np.array(pal_of(bytes(palb)), int)
    npal = len(P)
    # 후보 색 묶음 (위치 i = 팔레트 인덱스*2)
    pos4 = list(range(0, npal - 3, 2)); pos2 = list(range(0, npal - 1, 2))
    C4 = np.stack([P[i:i+4] for i in pos4]) if pos4 else np.zeros((0, 4, 3), int)
    C2 = np.stack([P[i:i+2] for i in pos2]) if pos2 else np.zeros((0, 2, 3), int)
    if len(C2):
        c0, c1 = C2[:, 0], C2[:, 1]
        M1 = np.stack([c0, c1, (c0 + c1) // 2], 1)
        M3 = np.stack([c0, c1, (5 * c0 + 3 * c1) // 8, (3 * c0 + 5 * c1) // 8], 1)
    def best_existing(X, has_t):
        # X: (m,3) 불투명 픽셀. 반환 (err, mode, palidx, cands)
        best = None
        sets = [(0, C4[:, :3], pos4), (1, M1, pos2)] if has_t else [(2, C4, pos4), (3, M3, pos2)]
        for mode, C, pos in sets:
            if len(C) == 0: continue
            d = ((X[None, :, None, :] - C[:, None, :, :]) ** 2).sum(3).min(2).sum(1)
            j = int(d.argmin())
            if best is None or d[j] < best[0]:
                best = (int(d[j]), mode, pos[j] // 2, C[j])
        return best
    for by in range(bh):
        for bx in range(bw):
            blk = a[by*4:by*4+4, bx*4:bx*4+4]; ob = orig[by*4:by*4+4, bx*4:bx*4+4]
            if np.array_equal(blk, ob): continue
            opaque = blk[..., 3] >= 128
            has_t = not opaque.all()
            X = blk[opaque][:, :3] if opaque.any() else np.zeros((1, 3), int)
            k = 3 if has_t else 4
            cents = kmeans(X, k)
            while len(cents) < k: cents.append(cents[-1])
            cents = [tuple(int(v) for v in c) for c in cents[:k]]
            new_err = int(((X[:, None, :] - np.array(cents)[None]) ** 2).sum(2).min(1).sum())
            ex = best_existing(X, has_t)
            if ex is not None and (PAL_GROW_TOL is None or ex[0] <= new_err + PAL_GROW_TOL * len(X)):
                err, mode, pidx, C = ex
                colors = [tuple(c) for c in C]
            else:
                mode = 0 if has_t else 2
                entry = b''.join(struct.pack('<H', to555(c)) for c in cents + ([(0, 0, 0)] if has_t else []))
                while len(palb) % 4: palb += bytes(1)
                pidx = len(palb) // 4; palb += entry
                colors = cents
            code = 0
            carr = np.array(colors[:k], int)
            for t in range(16):
                y, x = t // 4, t % 4
                if not opaque[y, x]: v = 3
                else: v = int(((carr - blk[y, x, :3]) ** 2).sum(1).argmin())
                code |= v << (t * 2)
            struct.pack_into('<I', tex, (by * bw + bx) * 4, code)
            struct.pack_into('<H', idx, (by * bw + bx) * 2, (mode << 14) | pidx)
    return bytes(tex) + bytes(idx) + bytes(palb)

def kmeans(cols, k):
    cols = np.asarray(cols, float)
    uniq = np.unique(cols, axis=0)
    if len(uniq) <= k: return [tuple(int(v) for v in u) for u in uniq]
    # 밝기 순 초기화
    order = uniq[np.argsort(uniq.sum(1))]
    cents = order[np.linspace(0, len(order) - 1, k).astype(int)]
    for _ in range(8):
        dd = ((cols[:, None, :] - cents[None]) ** 2).sum(2); lab = dd.argmin(1)
        for j in range(k):
            if (lab == j).any(): cents[j] = cols[lab == j].mean(0)
    return [tuple(int(round(v)) for v in c) for c in cents]

# ---------------- 편집 적용 ----------------
USE_GALMURI = True  # 이미지 글자를 갈무리(도트 글꼴)로 렌더
_GD = paths.FONTS
def galmuri_pick(e):
    """명세의 font/size를 갈무리 글꼴·원래 크기·정수 배율·굵게로 변환"""
    if e.get('galmuri'):  # 명세에서 갈무리 글꼴을 직접 지정: "Galmuri11" / "Galmuri11-Bold" / "Galmuri9" / "Galmuri14"
        g = e['galmuri']; nat = {'Galmuri7': 8, 'Galmuri9': 10, 'Galmuri11': 12, 'Galmuri11-Bold': 12, 'Galmuri14': 15}[g]
        return os.path.join(_GD, g + '.ttf'), nat, e.get('gscale', 1), e.get('bold', 0) if g == 'Galmuri14' else 0
    s = e.get('size', 12); boldface = e.get('font', 'malgunbd') == 'malgunbd' or e.get('bold', 0) > 0
    if s <= 10: return os.path.join(_GD, 'Galmuri9.ttf'), 10, 1, 0
    if s <= 13: return os.path.join(_GD, 'Galmuri11-Bold.ttf' if boldface else 'Galmuri11.ttf'), 12, 1, 0
    if s <= 17: return os.path.join(_GD, 'Galmuri14.ttf'), 15, 1, e.get('bold', 0)
    k = max(2, round(s / 12))
    return os.path.join(_GD, 'Galmuri11-Bold.ttf' if boldface else 'Galmuri11.ttf'), 12, k, 0

def draw_text(img, e):
    x, y, w, h = e['rect']
    gscale = 1
    if USE_GALMURI:
        gpath, gsize, gscale, gbold = galmuri_pick(e)
        e = dict(e, aa=False, bold=gbold, line_gap=round(e.get('line_gap', 0) / gscale))
        font = ImageFont.truetype(gpath, gsize)
    else:
        font = ImageFont.truetype(FONTS[e.get('font', 'malgunbd')], e.get('size', 12))
    lines = e['text'].split('\n')
    spacing = e.get('spacing', 0); gap = e.get('line_gap', 0)
    ow = e.get('outline_w', 1) if e.get('outline') else 0
    sh = e.get('shadow')
    pad = 4 + ow + (max(abs(sh[0]), abs(sh[1])) if sh else 0)
    asc, desc = font.getmetrics()
    lh = asc + desc + gap
    def line_w(t):
        return sum(font.getlength(c) + spacing for c in t) - (spacing if t else 0)
    tw = int(max(line_w(t) for t in lines)) + 1
    th = lh * len(lines)
    W, H = tw + pad * 2, th + pad * 2
    mask = Image.new('L', (W, H), 0); md = ImageDraw.Draw(mask)
    if not e.get('aa', True): md.fontmode = '1'
    # 실제 잉크 영역 기준 세로 정렬
    for i, t in enumerate(lines):
        cx = pad
        lw = line_w(t)
        if e.get('align', 'center') == 'center': cx = pad + (tw - lw) / 2
        elif e.get('align') == 'right': cx = pad + tw - lw
        for c in t:
            md.text((cx, pad + i * lh), c, font=font, fill=255)
            cx += font.getlength(c) + spacing
    for _ in range(e.get('bold', 0)):  # 가로 1px 굵게
        sh_m = Image.new('L', mask.size, 0); sh_m.paste(mask, (1, 0))
        mask = Image.fromarray(np.maximum(np.asarray(mask), np.asarray(sh_m)))
    if gscale > 1:
        mask = mask.resize((mask.width * gscale, mask.height * gscale), Image.NEAREST)
    bbox = mask.getbbox() or (0, 0, 1, 1)
    # 가로 압축 (rect 폭 초과 시)
    inkw = bbox[2] - bbox[0] + 2 * ow + (abs(sh[0]) if sh else 0)
    sx = min(1.0, (w) / inkw) if inkw > 0 else 1.0
    mask = mask.crop((bbox[0], bbox[1], bbox[2], bbox[3]))
    sy = e.get('scale_y', 1.0)  # 세로 배율 (게임에서 세로로 늘려 보이는 텍스처용)
    if sx < 1.0 or sy != 1.0:
        mask = mask.resize((max(1, int(mask.width * sx)), max(1, int(round(mask.height * sy)))), Image.LANCZOS)
        if USE_GALMURI:
            mask = mask.point(lambda v: 255 if v >= 110 else 0)
    mw, mh = mask.size
    fullw = mw + 2 * ow + (abs(sh[0]) if sh else 0); fullh = mh + 2 * ow + (abs(sh[1]) if sh else 0)
    al = e.get('align', 'center'); va = e.get('valign', 'middle')
    ox = x + (0 if al == 'left' else (w - fullw) // 2 if al == 'center' else w - fullw) + ow
    oy = y + (0 if va == 'top' else (h - fullh) // 2 if va == 'middle' else h - fullh) + ow
    layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
    def put(m, color, px_, py_):
        col = Image.new('RGBA', m.size, hexc(color) + (255,)); col.putalpha(m)
        big = Image.new('RGBA', img.size, (0, 0, 0, 0)); big.paste(col, (int(px_), int(py_)))
        layer.alpha_composite(big)
    def stamp(color, dx, dy):
        put(mask, color, ox + dx, oy + dy)
    padded = None
    if ow or sh:
        padded = Image.new('L', (mw + 2 * ow, mh + 2 * ow), 0); padded.paste(mask, (ow, ow))
        if ow: padded = dilate(padded, ow)
    if sh: put(padded, sh[2], ox - ow + sh[0], oy - ow + sh[1])
    if ow: put(padded, e['outline'], ox - ow, oy - ow)
    if e.get('color2'):
        top = np.array(hexc(e['color'])); bot = np.array(hexc(e['color2']))
        grad = Image.new('RGBA', mask.size)
        g = np.zeros((mh, mw, 4), np.uint8)
        for yy in range(mh):
            t = yy / max(1, mh - 1); g[yy, :, :3] = (top * (1 - t) + bot * t).astype(np.uint8)
        g[..., 3] = np.asarray(mask)
        layer.alpha_composite(Image.fromarray(g, 'RGBA'), (int(ox), int(oy)))
    else:
        stamp(e['color'], 0, 0)
    # 편집 영역 밖으로 번지지 않게 클립
    clip = Image.new('L', img.size, 0); ImageDraw.Draw(clip).rectangle([x - ow - 2, y - ow - 2, x + w + ow + 2, y + h + ow + 2], fill=255)
    la = np.asarray(layer).copy(); la[..., 3] = la[..., 3] * (np.asarray(clip) > 0)
    img.alpha_composite(Image.fromarray(la, 'RGBA'))

def dilate(mask, r):
    from PIL import ImageFilter
    m = mask
    for _ in range(r): m = m.filter(ImageFilter.MaxFilter(3))
    # 마스크가 커졌으므로 원점 보정 없이 동일 크기 유지(MaxFilter는 크기 유지) → 가장자리 잘림 방지 위해 패딩
    return m

def apply(img, spec):
    img = img.convert('RGBA'); src = img.copy()
    for e in spec.get('edits', []):
        op = e['op']
        if op == 'clear':
            x, y, w, h = e['rect']; ImageDraw.Draw(img).rectangle([x, y, x + w - 1, y + h - 1], fill=(0, 0, 0, 0))
        elif op == 'fill':
            x, y, w, h = e['rect']; ImageDraw.Draw(img).rectangle([x, y, x + w - 1, y + h - 1], fill=hexc(e['color']) + (255,))
        elif op == 'copy':
            x, y, w, h = e['src']; img.paste(src.crop((x, y, x + w, y + h)), tuple(e['dst']))
        elif op == 'hfill':
            x, y, w, h = e['rect']; col = src.crop((e['from_x'], y, e['from_x'] + 1, y + h))
            img.paste(col.resize((w, h), Image.NEAREST), (x, y))
        elif op == 'vfill':
            x, y, w, h = e['rect']; row = src.crop((x, e['from_y'], x + w, e['from_y'] + 1))
            img.paste(row.resize((w, h), Image.NEAREST), (x, y))
        elif op == 'text':
            draw_text(img, e)
    return img

def preview(before, after, out, scale=2):
    W = max(before.width, after.width) * scale
    H = (before.height + after.height) * scale + 6
    bg = Image.new('RGBA', (W, H), (60, 70, 90, 255))
    chk = Image.new('RGBA', before.size, (0, 0, 0, 0))
    for i, im in enumerate([before, after]):
        base = Image.new('RGBA', im.size, (60, 70, 90, 255)); base.alpha_composite(im.convert('RGBA'))
        bg.paste(base.resize((im.width * scale, im.height * scale), Image.NEAREST), (0, i * (before.height * scale + 6)))
    bg.convert('RGB').save(out)
