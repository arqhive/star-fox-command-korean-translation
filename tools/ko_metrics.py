"""한글 글리프 생성·폭 계산 공용 설정"""
import struct
from PIL import Image, ImageDraw, ImageFont
import nftr as nftrmod

H_EXTRA = 2          # 게임이 글자마다 더하는 것으로 추정되는 자간(px) — 폭 검사용
SPACE_ADV = 5
# BMG → 사용하는 NFTR (첫 번째가 폭 계산 기준)
FONTMAP = {
    'advertise': ['advertise'],
    'battle':    ['battle'],
    'enemy':     ['enemy'],
    'scenario':  ['scenario', 'scenaio'],
    'strategy':  ['strategy', 'atrategy'],
}
# 타일 높이별 한글 렌더 설정: (굴림 크기, y 오프셋, 한글 간격)
import os as _os
import paths as _paths
_FD = _paths.FONTS
# 타일 높이별 한글 렌더 설정: (글꼴 경로, 크기, y 오프셋, 한글 간격) — 갈무리(DS 스타일 도트 글꼴, OFL)
def font_cfg(th):
    if th <= 11: return (_os.path.join(_FD, 'Galmuri9.ttf'), 10, 0, 10)
    return (_os.path.join(_FD, 'Galmuri11.ttf'), 12, 2, 12)

_fonts = {}
def load_font(path, size):
    if (path, size) not in _fonts:
        _fonts[(path, size)] = ImageFont.truetype(path, size)
    return _fonts[(path, size)]

def render_glyph(ch, tw, th):
    fpath, size, yoff, hadv = font_cfg(th)
    im = Image.new('1', (tw + 8, th), 0)
    d = ImageDraw.Draw(im); d.fontmode = '1'
    d.text((0, yoff), ch, font=load_font(fpath, size), fill=1)
    bbox = im.getbbox()
    if 0xAC00 <= ord(ch) <= 0xD7A3:
        shift, adv = bbox[0], hadv
    else:
        shift = bbox[0] - 1 if bbox else 0
        adv = (bbox[2] - bbox[0] + 2) if bbox else SPACE_ADV
    px = im.load()
    bits = bytearray((tw * th + 7) // 8)
    for y in range(th):
        for x in range(tw):
            sx = x + shift
            if 0 <= sx < im.width and px[sx, y]:
                i = y * tw + x; bits[i // 8] |= 0x80 >> (i % 8)
    return bytes(bits), (0, adv, adv)

class FontInfo:
    def __init__(self, b):
        self.b = b
        self.cmap = nftrmod.parse(b)['cmap']
        cg = struct.unpack_from('<I', b, 0x20)[0] - 8
        self.tw, self.th = b[cg+8], b[cg+9]
        self.cw = struct.unpack_from('<I', b, 0x24)[0] - 8
    def jp_adv(self, ch):
        if ch == ' ': return 4
        try: code = int.from_bytes(ch.encode('cp932'), 'big')
        except UnicodeEncodeError: return None
        g = self.cmap.get(code)
        if g is None: return None
        l, w, a = struct.unpack_from('<bBB', self.b, self.cw + 0x10 + 3*g)
        return l + w
    def ko_adv(self, ch):
        if ch == ' ': return SPACE_ADV
        if 0xAC00 <= ord(ch) <= 0xD7A3: return font_cfg(self.th)[3]
        a = self.jp_adv(ch)
        if a is not None: return a
        return render_glyph(ch, self.tw, self.th)[1][2]
    def width(self, line, ko=True):
        f = self.ko_adv if ko else self.jp_adv
        return sum((f(c) or 15) + H_EXTRA for c in line)
