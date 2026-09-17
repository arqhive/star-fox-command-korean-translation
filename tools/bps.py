"""BPS 패치 생성/적용 (Flips·ROM Patcher JS 호환)

python bps.py create <원본> <수정본> <패치.bps>
python bps.py apply  <원본> <패치.bps> <출력>
"""
import sys, zlib


def _vint(n):
    out = bytearray()
    while True:
        x = n & 0x7F
        n >>= 7
        if n == 0:
            out.append(0x80 | x)
            return bytes(out)
        out.append(x)
        n -= 1


def _rvint(b, p):
    data, shift = 0, 1
    while True:
        x = b[p]; p += 1
        data += (x & 0x7F) * shift
        if x & 0x80:
            return data, p
        shift <<= 7
        data += shift


def create(src, dst, metadata=b''):
    out = bytearray(b'BPS1')
    out += _vint(len(src)) + _vint(len(dst)) + _vint(len(metadata)) + metadata
    i, n = 0, len(dst)
    while i < n:
        # 같은 위치의 원본 바이트와 같으면 SourceRead, 다르면 TargetRead
        same = i < len(src) and src[i] == dst[i]
        j = i
        while j < n and (j < len(src) and src[j] == dst[j]) == same:
            j += 1
        # 아주 짧은 일치 구간은 TargetRead에 합쳐 명령 수를 줄임
        if same and j - i < 4 and j < n:
            k = j
            while k < n and not (k < len(src) and src[k] == dst[k]):
                k += 1
            j = k
            same = False
        length = j - i
        if same:
            out += _vint(((length - 1) << 2) | 0)
        else:
            out += _vint(((length - 1) << 2) | 1) + dst[i:j]
        i = j
    out += zlib.crc32(src).to_bytes(4, 'little') + zlib.crc32(dst).to_bytes(4, 'little')
    out += zlib.crc32(out).to_bytes(4, 'little')
    return bytes(out)


def apply(src, patch):
    assert patch[:4] == b'BPS1', 'BPS 파일이 아님'
    assert zlib.crc32(patch[:-4]) == int.from_bytes(patch[-4:], 'little'), '패치 파일 손상'
    assert zlib.crc32(src) == int.from_bytes(patch[-12:-8], 'little'), '원본 롬이 다름 (CRC32 불일치)'
    p = 4
    ssize, p = _rvint(patch, p); tsize, p = _rvint(patch, p); msize, p = _rvint(patch, p); p += msize
    out = bytearray(tsize); o = 0; srel = trel = 0
    end = len(patch) - 12
    while p < end:
        d, p = _rvint(patch, p)
        cmd, length = d & 3, (d >> 2) + 1
        if cmd == 0:
            out[o:o+length] = src[o:o+length]; o += length
        elif cmd == 1:
            out[o:o+length] = patch[p:p+length]; p += length; o += length
        elif cmd == 2:
            off, p = _rvint(patch, p); srel += (-1 if off & 1 else 1) * (off >> 1)
            out[o:o+length] = src[srel:srel+length]; srel += length; o += length
        else:
            off, p = _rvint(patch, p); trel += (-1 if off & 1 else 1) * (off >> 1)
            for _ in range(length):
                out[o] = out[trel]; o += 1; trel += 1
    assert zlib.crc32(out) == int.from_bytes(patch[-8:-4], 'little'), '결과 CRC32 불일치'
    return bytes(out)


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'create':
        a = open(sys.argv[2], 'rb').read(); b = open(sys.argv[3], 'rb').read()
        pt = create(a, b)
        open(sys.argv[4], 'wb').write(pt)
        print('패치 생성:', sys.argv[4], len(pt), 'bytes')
    elif cmd == 'apply':
        a = open(sys.argv[2], 'rb').read(); pt = open(sys.argv[3], 'rb').read()
        open(sys.argv[4], 'wb').write(apply(a, pt))
        print('적용 완료:', sys.argv[4])
