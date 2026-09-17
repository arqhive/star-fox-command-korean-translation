# 스타폭스 커맨드 한글 패치 (NDS)

닌텐도 DS **스타폭스 커맨드 (일본판)** 의 비공식 한글 패치입니다.

- 대사 전체 한글화: 스토리·전투 무전·작전 화면·오프닝/엔딩·적 이름 (약 2,870문장)
- 이미지 글자 한글화: 메뉴·타이틀·스테이지 제목·갤러리·옵션·Wi-Fi 안내·작전 화면 등 496장
- 글꼴: DS 느낌의 도트 글꼴 **갈무리**
- 인물·지명 표기는 한국 정식 발매작(스타폭스 2026, 스타폭스 64 3D)을 따랐습니다
- 닉네임 입력 화면은 영문 자판이 기본으로 뜨도록 수정했습니다

## 패치 적용 방법

1. 원본 롬을 준비합니다. **반드시 아래와 같은 일본판 롬**이어야 합니다.

   | 항목 | 값 |
   |---|---|
   | 파일 | Star Fox Command (Japan).nds (ASFJ) |
   | 크기 | 33,554,432 bytes |
   | CRC32 | `618C4089` |
   | MD5 | `81d9550164d4c0a3756d1271ee063a1a` |
   | SHA-1 | `fe0a3ba974132de5d63429b48ee9d3e8b6d6a318` |

2. [릴리즈](../../releases)에서 `StarFoxCommand_KO_v*.bps` 를 받습니다.
3. BPS 패치 도구로 적용합니다.
   - 웹: [ROM Patcher JS](https://www.marcrobledo.com/RomPatcher.js/)
   - PC: Floating IPS (Flips)
   - 또는 이 저장소의 스크립트: `python bps.py apply "Star Fox Command (Japan).nds" StarFoxCommand_KO_v1.0.bps "Star Fox Command (KO).nds"`
4. 에뮬레이터(melonDS 등)나 플래시카트에서 실행합니다.

## 알려진 문제 (v1.0)

- 일부 작은 이름 목록(칸 높이 7~9px)은 받침이 많은 글자가 뭉개져 보일 수 있습니다.
- 여러 조각을 조합해 보여주는 이미지(라운드 정보, 작전 설명 일부)는 화면에 따라 어색할 수 있습니다.
- 닉네임은 영문·기호만 입력할 수 있습니다(한글 입력 미지원).
- `corneria.bmg`(게임에서 쓰이지 않는 것으로 보이는 옛 대사 파일)는 번역하지 않았습니다.

이상한 화면을 발견하면 스크린샷과 함께 이슈로 알려 주세요.

## 직접 빌드하기

Python 3.10+ 와 `pillow`, `numpy` 가 필요합니다.

```bash
pip install pillow numpy
```

일본판 롬을 `rom/Star Fox Command (Japan).nds` 에 두거나 환경 변수 `SFC_JP_ROM` 으로 경로를 지정한 뒤:

```bash
python build.py
```

결과는 `out/Star Fox Command (Japan) [KO].nds` 에 생성됩니다. 패치 파일 만들기:

```bash
python bps.py create "rom/Star Fox Command (Japan).nds" "out/Star Fox Command (Japan) [KO].nds" out/StarFoxCommand_KO.bps
```

### 폴더 구조

| 경로 | 내용 |
|---|---|
| `trans/ko/*.json` | 한국어 번역 (BMG 메시지 인덱스 → 문장) |
| `trans/GLOSSARY.md` | 용어집·말투·표기 규칙 |
| `img/spec/**/*.json` | 이미지별 편집 명세 (지울 영역, 넣을 글자, 글꼴·색) |
| `img/AGENT_GUIDE.md` | 이미지 명세 작성 가이드 |
| `fonts/` | 갈무리 글꼴 (SIL OFL 1.1) |
| `build.py` | 대사·글꼴·이미지·코드 패치를 원본 롬에 적용 |
| `check_ko.py` | 번역 검사 (줄 수, 화면 폭, `@1` 치환기호 등) — `python export_src.py` 로 원문을 먼저 추출 |
| `imgtool.py` | 이미지 확인/미리보기 (`info`, `render`) |
| `ndsfs.py` `lz.py` `blz.py` `bmg.py` `nftr.py` `texdec.py` `bg2d.py` `texlib.py` | NDS 파일시스템·압축·텍스트·글꼴·텍스처 포맷 처리 |
| `bps.py` | BPS 패치 생성/적용 |

### 기술 메모

- 대사: `2D/MessageText/*.bmg` (Shift-JIS). 한글 음절을 쓰지 않는 SJIS 코드에 배정하고, 파일별 서브셋 글꼴(NFTR)에 글리프를 추가합니다. 글꼴의 마지막 전체범위 CMAP 블록에 병합해야 게임이 찾습니다.
- 이미지: `3D/Textures/**/*.ntfq` 는 헤더가 없어 파일 크기로 형식(COMP4x4/PLTT4·16·256/A5I3·A3I5)과 크기를 판정합니다(`texchoice.json`). COMP4x4 는 **팔레트를 늘리면 실기에서 다른 텍스처 색이 깨지므로** 기존 색 묶음만 재사용합니다.
- 코드 패치: 오버레이 4 `+0x233a8` (닉네임 자판 기본 모드를 영문으로).

## 크레딧·라이선스

- 한글화 작업: arqhive
- 글꼴: [갈무리 (Galmuri)](https://github.com/quiple/galmuri) © Lee Minseo — SIL Open Font License 1.1 (`fonts/OFL.txt`)
- 이 저장소의 스크립트: MIT License (`LICENSE`)
- 스타폭스 커맨드는 Nintendo의 저작물입니다. 이 저장소에는 게임 롬이나 원문 데이터가 포함되어 있지 않으며, 정품을 소유한 분만 이용해 주세요.

## 면책조항

- 이 패치는 팬이 비영리 목적으로 만든 **비공식** 한글 패치이며, Nintendo, Q-Games 및 관련 권리자와 아무런 관계가 없고 이들의 승인·보증을 받지 않았습니다.
- Star Fox, 스타폭스 및 관련 명칭·캐릭터·이미지의 권리는 각 권리자에게 있습니다.
- 이 저장소와 릴리즈는 게임 롬을 포함하거나 배포하지 않습니다. 패치는 이용자가 **직접 소유한 정품 게임**에서 추출한 롬에만 적용해 주세요. 롬의 불법 다운로드·공유는 허용하지 않으며, 관련 요청에는 응하지 않습니다.
- 패치된 롬을 배포하거나 판매하지 마세요. 이 패치를 유료로 판매하거나 상업적으로 이용하는 것을 금지합니다.
- 이 패치는 "있는 그대로" 제공되며, 사용으로 인해 발생하는 세이브 데이터 손실, 기기·에뮬레이터 문제 등 어떠한 손해에 대해서도 제작자는 책임지지 않습니다. 적용 전 원본 롬과 세이브 파일을 반드시 백업해 주세요.
- 권리자의 요청이 있을 경우 이 저장소와 배포물은 사전 예고 없이 삭제될 수 있습니다.
