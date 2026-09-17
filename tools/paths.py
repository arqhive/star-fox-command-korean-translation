"""경로 설정 — 저장소 구조와 원본 롬 위치를 한곳에서 정한다.

원본 롬은 환경 변수(SFC_JP_ROM / SFC_US_ROM) → `rom/` 폴더 → 저장소 상위 폴더 순으로 찾는다.
"""
import os

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)                      # 저장소 루트
TRANSLATION = os.path.join(ROOT, 'translation')    # 한국어 번역·이미지 명세
IMAGES = os.path.join(TRANSLATION, 'images')
FONTS = os.path.join(ROOT, 'fonts')
WORK = os.path.join(ROOT, 'work')                  # 원문 추출·미리보기·빌드 결과 (커밋 안 함)

JP_NAME = 'Star Fox Command (Japan).nds'
US_NAME = 'Star Fox Command (USA, Australia).nds'


def _find(env, name):
    if os.environ.get(env):
        return os.environ[env]
    for d in (os.path.join(ROOT, 'rom'), os.path.dirname(ROOT)):
        p = os.path.join(d, name)
        if os.path.exists(p):
            return p
    return os.path.join(ROOT, 'rom', name)


JP_ROM = _find('SFC_JP_ROM', JP_NAME)              # 필수: 일본판 원본
US_ROM = _find('SFC_US_ROM', US_NAME)              # 선택: 번역 참고용 북미판
OUT_ROM = os.environ.get('KO_OUT', os.path.join(WORK, 'Star Fox Command (Japan) [KO].nds'))
