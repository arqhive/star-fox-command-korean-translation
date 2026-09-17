import struct
def blz_dec(data):
    """NDS arm9 backward LZ 해제 (압축부 끝에 footer: u32 [bufferTopAndBottom], u32 extra size)"""
    d = bytearray(data)
    bt, extra = struct.unpack_from('<II', d, len(d) - 8)
    top = bt & 0xFFFFFF; bottom = bt >> 24
    out = bytearray(d) + bytearray(extra)
    src = len(d) - bottom
    dst = len(out)
    end = len(d) - top
    while src > end:
        src -= 1; flags = d[src]
        for i in range(8):
            if src <= end: break
            if flags & 0x80:
                src -= 2
                v = d[src + 1] << 8 | d[src]
                n = (v >> 12) + 3; disp = (v & 0xFFF) + 3
                for _ in range(n):
                    dst -= 1; out[dst] = out[dst + disp]
            else:
                src -= 1; dst -= 1; out[dst] = d[src]
            flags <<= 1
            if dst <= end: break
    return bytes(out[:len(out)])
