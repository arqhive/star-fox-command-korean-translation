"""롬 안의 파일을 바로 읽는 도우미 (추출 폴더 불필요)"""
import os
from ndsfs import parse
from lz import lz10_dec
import paths

_cache = {}
def rom(path=None):
    path = path or paths.JP_ROM
    if path not in _cache: _cache[path] = parse(path)
    return _cache[path]

def read(name, rompath=None):
    """name: 롬 내부 경로('-cmp'는 생략 가능). 압축이면 해제해서 반환"""
    d, h, files = rom(rompath)
    for k in (name + '-cmp', name):
        if k in files:
            fid, s, e = files[k]
            b = d[s:e]
            return lz10_dec(b) if k.endswith('-cmp') else b
    raise KeyError(name)
