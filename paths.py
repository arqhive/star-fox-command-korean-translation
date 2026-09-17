"""롬 경로 설정 — 환경 변수 또는 기본 위치(rom/ 폴더 → 상위 폴더 순)에서 찾는다."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
JP_NAME = 'Star Fox Command (Japan).nds'
US_NAME = 'Star Fox Command (USA, Australia).nds'


def _find(env, name):
    if os.environ.get(env):
        return os.environ[env]
    for d in (os.path.join(HERE, 'rom'), os.path.join(HERE, '..')):
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return os.path.join(HERE, 'rom', name)


JP_ROM = _find('SFC_JP_ROM', JP_NAME)          # 필수: 일본판 원본
US_ROM = _find('SFC_US_ROM', US_NAME)          # 선택: 번역 참고용 북미판
OUT_ROM = os.environ.get('KO_OUT', os.path.join(HERE, 'out', 'Star Fox Command (Japan) [KO].nds'))
