"""2D BG 그림 (nbfc 4bpp 8x8 타일 / nbfs 16bit 맵 / nbfp 16색 팔레트) 디코드·인코드"""
import struct, numpy as np, json, os
from PIL import Image
from texdec import rgb555
from lz import lz10_dec

def load(rom, base):
    d, h, files = rom
    def get(ext):
        for k in (base + '.' + ext + '-cmp', base + '.' + ext):
            if k in files:
                fid, s, e = files[k]; b = d[s:e]
                return (lz10_dec(b) if k.endswith('-cmp') else b), k
        return None, None
    chr_, kc = get('nbfc'); scr, ks = get('nbfs'); pal, kp = get('nbfp')
    return chr_, scr, pal, (kc, ks, kp)

def palette(pal):
    return [rgb555(struct.unpack_from('<H', pal, i)[0]) for i in range(0, len(pal) // 2 * 2, 2)]

def tiles_of(chr_):
    n = len(chr_) // 32
    t = np.zeros((n, 8, 8), np.uint8)
    for i in range(n):
        for p in range(64):
            t[i, p // 8, p % 8] = (chr_[i * 32 + p // 2] >> (4 * (p % 2))) & 15
    return t

def decode(chr_, scr, pal, tw):
    """tw: 맵 가로 타일 수. scr 없으면 타일을 순서대로 배치"""
    pl = palette(pal); T = tiles_of(chr_)
    if scr is not None:
        ents = struct.unpack('<%dH' % (len(scr) // 2), scr[:len(scr) // 2 * 2])
    else:
        ents = list(range(len(T)))
    th = (len(ents) + tw - 1) // tw
    idx = np.zeros((th * 8, tw * 8), np.uint8)
    for k, e in enumerate(ents):
        ti = e & 0x3ff; t = T[ti] if ti < len(T) else np.zeros((8, 8), np.uint8)
        if e & 0x400: t = t[:, ::-1]
        if e & 0x800: t = t[::-1, :]
        y, x = divmod(k, tw); idx[y * 8:y * 8 + 8, x * 8:x * 8 + 8] = t
    rgba = np.zeros(idx.shape + (4,), np.uint8)
    for v in range(16):
        c = pl[v] if v < len(pl) else (255, 0, 255)
        m = idx == v; rgba[m, :3] = c; rgba[m, 3] = 0 if v == 0 else 255
    return Image.fromarray(rgba, 'RGBA')

def encode(chr_, scr, pal, tw, img):
    pl = np.array(palette(pal), int)
    a = np.asarray(img.convert('RGBA')).astype(int)
    H, W = a.shape[:2]
    idx = np.zeros((H, W), np.uint8)
    op = a[..., 3] >= 128
    flat = a[..., :3].reshape(-1, 3)
    d2 = ((flat[:, None, :] - pl[None, 1:, :]) ** 2).sum(2)
    idx = (d2.argmin(1) + 1).reshape(H, W).astype(np.uint8); idx[~op] = 0
    if scr is None:
        n = len(chr_) // 32; out = bytearray(len(chr_))
        for i in range(n):
            y, x = divmod(i, tw)
            t = idx[y * 8:y * 8 + 8, x * 8:x * 8 + 8]
            for p in range(64):
                out[i * 32 + p // 2] |= int(t[p // 8, p % 8]) << (4 * (p % 2))
        return bytes(out), None
    # 맵 재구성: 기존 엔트리의 팔레트 비트 유지, 타일은 중복 제거하며 새로 생성
    ents = list(struct.unpack('<%dH' % (len(scr) // 2), scr[:len(scr) // 2 * 2]))
    tiles = []; lut = {}
    def add(t):
        key = t.tobytes()
        if key in lut: return lut[key], 0
        for fl, tt in ((0x400, t[:, ::-1]), (0x800, t[::-1, :]), (0xC00, t[::-1, ::-1])):
            if tt.tobytes() in lut: return lut[tt.tobytes()], fl
        lut[key] = len(tiles); tiles.append(t.copy()); return lut[key], 0
    add(np.zeros((8, 8), np.uint8))  # 0번 타일은 빈 타일 유지
    newe = []
    for k, e in enumerate(ents):
        y, x = divmod(k, tw)
        t = idx[y * 8:y * 8 + 8, x * 8:x * 8 + 8]
        ti, fl = add(t)
        newe.append((e & 0xF000) | fl | ti)
    out = bytearray(len(tiles) * 32)
    for i, t in enumerate(tiles):
        for p in range(64):
            out[i * 32 + p // 2] |= int(t[p // 8, p % 8]) << (4 * (p % 2))
    return bytes(out), struct.pack('<%dH' % len(newe), *newe) + scr[len(newe) * 2:]
