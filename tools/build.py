import struct, json, glob, os, sys
from ndsfs import parse
from lz import lz10_dec, lz10_comp
import nftr as nftrmod
from ko_metrics import render_glyph, SPACE_ADV, FONTMAP

import paths
SRC = paths.JP_ROM
DST = paths.OUT_ROM
os.chdir(paths.ROOT)
MT = '2D/MessageText/'

rom, hdr, files = parse(SRC)
rom = bytearray(rom)

def getfile(path):
    fid, s, e = files[path]
    b = bytes(rom[s:e])
    return lz10_dec(b) if path.endswith('-cmp') else b

# ---------- NFTR ----------
def sjis_candidates():
    for lead in list(range(0x88, 0xA0)) + list(range(0xE0, 0xEB)):
        for tr in range(0x40, 0xFD):
            if tr == 0x7F: continue
            yield lead << 8 | tr

def rebuild_nftr(b, newglyphs):
    """newglyphs: list of (code, ch). 기존 섹션 유지 + 글리프/폭 추가 + 전체범위 type2 CMAP에 병합"""
    secs = []
    p = 16
    while p < len(b):
        mag = b[p:p+4]; sz = struct.unpack_from('<I', b, p+4)[0]
        secs.append([mag, bytearray(b[p:p+sz]), p]); p += sz
    finf = next(s for s in secs if s[0] == b'FNIF')[1]
    cglp = next(s for s in secs if s[0] == b'PLGC')[1]
    cwdh = next(s for s in secs if s[0] == b'HDWC')[1]
    cmaps = [s for s in secs if s[0] == b'PAMC']
    tw, th, tsize = cglp[8], cglp[9], struct.unpack_from('<H', cglp, 10)[0]
    nold = (len(cglp) - 0x10) // tsize
    last = struct.unpack_from('<H', cwdh, 10)[0]
    assert last + 1 == nold and struct.unpack_from('<I', cwdh, 12)[0] == 0
    # 기존 글리프 영역을 정확한 길이로 자르기(패딩 제거)
    body = bytearray(cglp[0x10:0x10 + nold * tsize])
    wd = bytearray(cwdh[0x10:0x10 + nold * 3])
    pairs = []
    for i, (code, ch) in enumerate(newglyphs):
        bits, cw = render_glyph(ch, tw, th)
        body += bits[:tsize].ljust(tsize, b'\0')
        wd += struct.pack('<bBB', *cw)
        pairs.append((code, nold + i))
    # ASCII 공백 폭을 한국어 띄어쓰기에 맞게 넓힘
    cm = nftrmod.parse(b)['cmap']
    sp = cm.get(0x20)
    if sp is not None:
        wd[sp*3:sp*3+3] = struct.pack('<bBB', SPACE_ADV, 0, SPACE_ADV)
    def pad4(x):
        while len(x) % 4: x.append(0)
        return x
    new_cglp = pad4(bytearray(cglp[:0x10]) + body)
    struct.pack_into('<I', new_cglp, 4, len(new_cglp))
    new_cwdh = bytearray(cwdh[:0x10]) + wd
    struct.pack_into('<H', new_cwdh, 10, nold + len(newglyphs) - 1)
    new_cwdh = pad4(new_cwdh); struct.pack_into('<I', new_cwdh, 4, len(new_cwdh))
    # 기존 CMAP 중 새 코드를 범위로 덮는 type2 블록에 병합 (게임은 범위가 맞는 첫 블록에서 검색을 끝냄)
    cmap_blocks = [bytearray(s[1]) for s in cmaps]
    ranges = [struct.unpack_from('<HHH', blk, 8) for blk in cmap_blocks]
    groups = {}
    for code, g in pairs:
        i = next((i for i, (lo, hi, _) in enumerate(ranges) if lo <= code <= hi), None)
        assert i is not None and ranges[i][2] == 2, 'type2 블록이 아닌 곳에 걸림: %x' % code
        groups.setdefault(i, []).append((code, g))
    for i, add in groups.items():
        blk = cmap_blocks[i]
        cnt = struct.unpack_from('<H', blk, 0x14)[0]
        ent = sorted([struct.unpack_from('<HH', blk, 0x16 + 4*k) for k in range(cnt)] + add)
        nb = bytearray(blk[:0x14]) + struct.pack('<H', len(ent))
        for c, g in ent: nb += struct.pack('<HH', c, g)
        cmap_blocks[i] = pad4(nb)
        struct.pack_into('<I', cmap_blocks[i], 4, len(cmap_blocks[i]))
    # 재조립
    out = bytearray(b[:16])
    finf_pos = len(out); out += finf
    cglp_pos = len(out); out += new_cglp
    cwdh_pos = len(out); out += new_cwdh
    cmap_pos = []
    for blk in cmap_blocks:
        cmap_pos.append(len(out)); out += blk
    for i, pos in enumerate(cmap_pos):
        nxt = cmap_pos[i+1] + 8 if i + 1 < len(cmap_pos) else 0
        struct.pack_into('<I', out, pos + 0x10, nxt)
    struct.pack_into('<III', out, finf_pos + 0x10, cglp_pos + 8, cwdh_pos + 8, cmap_pos[0] + 8)
    struct.pack_into('<I', out, 8, len(out))
    struct.pack_into('<H', out, 14, 3 + len(cmap_blocks))
    return bytes(out)

# ---------- BMG ----------
def rebuild_bmg(b, trans, enc):
    E = '>'
    assert b[:8] == b'MESGbmg1'
    ip = 0x20; isz = struct.unpack_from(E+'I', b, ip+4)[0]
    dp = ip + isz; dsz = struct.unpack_from(E+'I', b, dp+4)[0]
    n, es = struct.unpack_from(E+'HH', b, ip+8)
    inf = bytearray(b[ip:ip+isz])
    old = b[dp+8:dp+dsz]
    def old_string(off):
        q = off
        while old[q] != 0:
            if old[q] == 0x1A: q += old[q+1]
            elif 0x81 <= old[q] <= 0x9F or 0xE0 <= old[q] <= 0xFC: q += 2
            else: q += 1
        return old[off:q]
    # 쓰이지 않는 옛 문자열을 버리고 DAT1을 새로 구성 (같은 문자열은 공유)
    dat = bytearray(b'\0')
    pool = {b'': 0}
    for idx in range(n):
        off = struct.unpack_from(E+'I', inf, 0x10 + idx*es)[0]
        s = enc(trans[idx]) if idx in trans else old_string(off)
        if s not in pool:
            pool[s] = len(dat); dat += s + b'\0'
        struct.pack_into(E+'I', inf, 0x10 + idx*es, pool[s])
    blk = bytearray(b'DAT1\0\0\0\0') + dat
    while len(blk) % 32: blk.append(0)
    struct.pack_into(E+'I', blk, 4, len(blk))
    out = bytearray(b[:0x20]) + inf + blk
    struct.pack_into(E+'I', out, 8, len(out))
    return bytes(out)

# ---------- 번역 로드 ----------
TRANS = {}
for fn in sorted(glob.glob(os.environ.get('KO_DIR', 'translation/ko') + '/*.json')):
    name = os.path.basename(fn)[:-5]
    data = json.load(open(fn, encoding='utf-8'))
    for k, v in data.items():
        if ':' in k: f, i = k.split(':')
        else: f, i = name.rsplit('_', 1)[0], k
        TRANS.setdefault(f, {})[int(i)] = v
for f, t in TRANS.items(): print(f, len(t), '항목')

def crc16(data):
    crc = 0xFFFF
    for x in data:
        crc ^= x
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc

newdata = {}
for bmgname, trans in TRANS.items():
    fonts = {fn: getfile(MT + fn + '.nftr-cmp') for fn in FONTMAP[bmgname]}
    cmaps = {fn: nftrmod.parse(f)['cmap'] for fn, f in fonts.items()}
    used = set().union(*[set(c) for c in cmaps.values()])
    need = []
    seen = set()
    for t in trans.values():
        for ch in t:
            if ch == '\n' or ch in seen: continue
            seen.add(ch)
            try:
                code = int.from_bytes(ch.encode('cp932'), 'big')
                if all(code in c for c in cmaps.values()): continue
            except UnicodeEncodeError:
                pass
            need.append(ch)
    cand = (c for c in sjis_candidates() if c not in used)
    codemap = {ch: next(cand) for ch in need}
    def enc(text):
        o = bytearray()
        for ch in text:
            if ch == '\n': o.append(0x0A)
            elif ch in codemap: o += codemap[ch].to_bytes(2, 'big')
            else: o += ch.encode('cp932')
        return bytes(o)
    glyphs = [(codemap[ch], ch) for ch in need]
    for fn, f in fonts.items():
        newdata[MT + fn + '.nftr-cmp'] = lz10_comp(rebuild_nftr(f, glyphs))
    newdata[MT + bmgname + '.bmg-cmp'] = lz10_comp(rebuild_bmg(getfile(MT + bmgname + '.bmg-cmp'), trans, enc))
    print(f'{bmgname}: 번역 {len(trans)}개, 새 글리프 {len(need)}')

# ---------- 이미지 (translation/images/**/*.json) ----------
if os.environ.get('NO_IMG') != '1':
    import imgtool
    nimg = 0
    for sp in sorted(glob.glob('translation/images/**/*.json', recursive=True)):
        rel = os.path.relpath(sp, 'translation/images').replace(os.sep, '/')[:-5]
        try:
            kind, img, ctx = imgtool.load_any(rel)
        except Exception as ex:
            print('  [경고] 이미지 로드 실패:', rel, ex); continue
        spec = json.load(open(sp, encoding='utf-8'))
        new = imgtool.texlib.apply(img, spec)
        for path, data in imgtool.encode_any(kind, ctx, new).items():
            newdata[path] = lz10_comp(data) if path.endswith('-cmp') else data
        nimg += 1
    print(f'이미지 {nimg}개 적용')

romsize = hdr['romsize']
pos = (romsize + 3) & ~3
inplace = appended = 0
for path, data in newdata.items():
    fid, s0, e0 = files[path]
    if len(data) <= e0 - s0:
        # 원래 자리에 들어가면 덮어쓰기
        rom[s0:s0+len(data)] = data
        struct.pack_into('<II', rom, hdr['fat_off'] + fid*8, s0, s0 + len(data))
        inplace += 1
        continue
    if pos + len(data) > len(rom):
        rom.extend(b'\xff' * (0x4000000 - len(rom)))  # 64MB로 확장
    rom[pos:pos+len(data)] = data
    struct.pack_into('<II', rom, hdr['fat_off'] + fid*8, pos, pos + len(data))
    pos = (pos + len(data) + 3) & ~3
    appended += 1
assert pos <= len(rom), '롬 크기 초과'

# ---------- 코드 패치 ----------
# 닉네임 자판: 본체 언어가 일본어여도 영문 자판(모드 1)을 기본으로 (ov04 +0x233a8: bne → b 0x2202ae8)
_ovt = rom[hdr['ov9_off']:hdr['ov9_off'] + hdr['ov9_size']]
_fid = struct.unpack_from('<I', _ovt, 4 * 32 + 24)[0]
_s = struct.unpack_from('<I', rom, hdr['fat_off'] + _fid * 8)[0]
assert rom[_s + 0x233a6:_s + 0x233aa] == bytes.fromhex('002804d1'), '자판 패치 위치 불일치'
rom[_s + 0x233a8:_s + 0x233aa] = bytes.fromhex('0ee0')
print('코드 패치: 닉네임 자판 기본 영문')

# 배너(메뉴에 보이는 게임 이름) — 6개 언어 칸 모두 한국어로, 배너 CRC16 갱신
_bo = struct.unpack_from('<I', rom, 0x68)[0]
_bver = struct.unpack_from('<H', rom, _bo)[0]
assert _bver == 1, '배너 버전 예상과 다름: %#x' % _bver
BANNER_TITLE = '스타폭스 커맨드\nNintendo'
for _i in range(6):
    _p = _bo + 0x240 + 0x100 * _i
    rom[_p:_p + 0x100] = BANNER_TITLE.encode('utf-16-le').ljust(0x100, b'\0')
struct.pack_into('<H', rom, _bo + 2, crc16(rom[_bo + 0x20:_bo + 0x840]))
print('배너 이름:', BANNER_TITLE.replace('\n', ' / '))
print(f'파일 배치: 제자리 {inplace}개, 끝에 추가 {appended}개')
if len(rom) > 0x2000000:
    rom[0x14] = max(rom[0x14], 9)  # 카트 용량 512Mbit
struct.pack_into('<I', rom, 0x80, pos)
struct.pack_into('<H', rom, 0x15E, crc16(rom[:0x15E]))
os.makedirs(os.path.dirname(os.path.abspath(DST)), exist_ok=True)
open(DST, 'wb').write(rom)
print('저장:', DST, '사용 크기', hex(pos))
