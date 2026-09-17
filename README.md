# 스타폭스 커맨드 한글 패치

*Star Fox Command* (닌텐도 DS, 일본판 `ASFJ`) 비공식 한국어 팬 패치입니다.
대사는 일본어판 원문을 기준으로 번역했습니다.

**제작: arqhive**

- 대사 전체 한글화 (약 2,870문장 — 스토리, 전투 무전, 작전 화면, 오프닝·엔딩, 적 이름)
- 그림 글씨 한글화 496장 (메뉴, 타이틀, 스테이지 제목, 갤러리, 옵션, Wi-Fi 안내, 작전 화면, 캐릭터 이름표)
- 글꼴: 닌텐도 DS 글꼴 디자인 기반 도트 글꼴 **갈무리**
- 인물·지명은 한국 정식 발매작(스타폭스 2026, 스타폭스 64 3D) 표기 기준 — 안돌프, 팔코 람바디, 라일라트, 카티나
- 닉네임 입력 화면이 영문 자판으로 시작하도록 코드 패치
- **원본과 같은 32MB 롬 크기 유지** (롬 확장 없음)
- 확인 환경: melonDS (스토리 진행, 작전·전투·결과 화면, 갤러리, 옵션까지 확인)

> 이 저장소에는 **게임 데이터(롬, 추출한 원문 대사, 그래픽, 스크린샷)가 들어 있지 않습니다.**
> 패치를 만들거나 적용하려면 본인이 소유한 게임에서 직접 덤프한 원본이 필요합니다.

## 사용자용: 패치 적용

[`release/`](release/) 폴더의 `.bps` 패치와 [`README_한국어.txt`](release/README_한국어.txt)를 참고하세요.
[릴리즈 페이지](../../releases)에서도 같은 파일을 받을 수 있습니다.

| 원본 (일본판) | 값 |
|---|---|
| 파일명 예 | `Star Fox Command (Japan).nds` |
| 크기 | 33,554,432 바이트 |
| CRC32 | `618C4089` |
| MD5 | `81d9550164d4c0a3756d1271ee063a1a` |
| SHA1 | `fe0a3ba974132de5d63429b48ee9d3e8b6d6a318` |

| 패치 적용 결과 | 값 |
|---|---|
| 크기 | 33,554,432 바이트 (원본과 같음) |
| CRC32 | `94FAF9E5` |
| MD5 | `ca5a5197570c7d03aacc033487d2f9f4` |
| SHA1 | `d7a185c981dcc38ece1d21bc0f96fbed97bf8986` |

- 북미·유럽판 롬에는 적용할 수 없습니다. 이전 버전 패치를 적용한 롬에 덧씌울 수도 없습니다.
- 패치 도구: [ROM Patcher JS](https://www.marcrobledo.com/RomPatcher.js/)(웹), Floating IPS(PC), 또는 이 저장소의 `tools/bps.py`.
- 확인: melonDS. 실기(DS·DSi·3DS + 플래시카트)는 **확인하지 않았습니다.**

### 알려진 문제

- 일부 작은 이름 목록(칸 높이 7~9px)은 받침이 많은 글자가 뭉개져 보일 수 있습니다.
- 여러 조각을 조합해 보여주는 이미지(라운드 정보 등)는 화면에 따라 어색할 수 있습니다.
- 닉네임은 영문·기호만 입력할 수 있습니다(한글 입력 미지원).
- 게임에서 쓰이지 않는 것으로 보이는 옛 대사 파일(`corneria.bmg`)은 번역하지 않았습니다.

이상한 화면이나 어색한 문장을 발견하면 이슈로 알려 주세요.

## 개발자용: 직접 빌드

### 요구 사항
- Python 3.10 이상, [Pillow](https://pypi.org/project/pillow/), [NumPy](https://pypi.org/project/numpy/)
- 원본 일본판 롬 (위 해시와 일치하는 파일)
- 글꼴은 저장소의 [`fonts/`](fonts/)(갈무리 TTF)를 쓰므로 OS 폰트와 무관하게 같은 결과가 나옵니다.

```bash
pip install pillow numpy
```

### 빌드
원본 롬을 `rom/Star Fox Command (Japan).nds` 에 두거나 환경 변수 `SFC_JP_ROM` 으로 경로를 지정한 뒤:

```bash
python tools/build.py
python tools/bps.py create "rom/Star Fox Command (Japan).nds" "work/Star Fox Command (Japan) [KO].nds" release/StarFoxCommand_KO.bps
```

결과는 `work/Star Fox Command (Japan) [KO].nds` 에 생성되며, 위 "패치 적용 결과" 해시와 바이트 단위로 같습니다.

`build.py`는 다음을 수행합니다.

1. `translation/ko/*.json` 의 한국어 대사를 BMG(`2D/MessageText/*.bmg`)에 다시 기록 — 쓰이지 않게 된 옛 일본어 문자열은 버리고 문자열 영역을 새로 구성
2. 번역에 쓰인 한글 음절을 사용되지 않는 Shift-JIS 코드에 배정하고, 파일별 서브셋 글꼴(NFTR)에 갈무리 글리프를 추가
3. `translation/images/**/*.json` 명세대로 텍스처(`3D/Textures/**/*.ntfq`)와 2D 타일 그림(`2D/**/*.nbfc`)의 일본어를 지우고 한글을 그려 원래 형식으로 재인코딩
4. 오버레이 4의 분기 2바이트를 고쳐 닉네임 자판 기본 모드를 영문으로 변경
5. 파일을 제자리(들어가면) 또는 롬 끝에 배치하고 FAT·사용 크기·헤더 체크섬 갱신

### 번역 작업

```bash
python tools/export_src.py          # work/src/*.json 에 일본어 원문 추출 (원문이므로 커밋 금지)
python tools/check_ko.py scenario_1 # 줄 수·화면 폭·@1 치환기호·일본어 잔여 검사
```

- 대사: [`translation/ko/*.json`](translation/ko) — `{"메시지 번호": "번역문"}`. 줄바꿈은 `\n`, `@1`은 플레이어 이름 치환기호.
  묶음은 `scenario_1~4`(스토리), `battle_1~2`(전투 무전·튜토리얼), `strategy_1~2`(작전 화면), `advertise_enemy`(오프닝·엔딩, 적 이름).
- 용어·말투: [`translation/GLOSSARY.md`](translation/GLOSSARY.md)
- 문장 부호·문체 검수 기준: [`docs/PUNCT_GUIDE.md`](docs/PUNCT_GUIDE.md), [`docs/COMMA_GUIDE.md`](docs/COMMA_GUIDE.md), [`docs/NATURAL_GUIDE.md`](docs/NATURAL_GUIDE.md)

### 그림 글씨 작업

```bash
python tools/imgtool.py info   Menu/General/menu_all   # 형식·크기·팔레트 출력 + 확대 격자 이미지
python tools/imgtool.py render Menu/General/menu_all   # 명세 적용 → 게임 형식 변환 → 결과 미리보기
```

- 명세: [`translation/images/**/*.json`](translation/images) — 이미지마다 지울 영역(`clear`/`fill`/`hfill`/`copy`)과 넣을 글자(`text`: 글꼴·크기·색·외곽선·정렬)를 정의합니다.
- 작성 방법: [`docs/IMAGE_GUIDE.md`](docs/IMAGE_GUIDE.md)
- 결과 미리보기는 `work/img/` 에 저장됩니다(커밋하지 않음).

### 폴더 구조

| 경로 | 내용 |
|---|---|
| `translation/ko/` | 한국어 대사 (BMG 메시지 번호 → 문장) |
| `translation/images/` | 이미지별 편집 명세 |
| `translation/GLOSSARY.md` | 용어집·말투·표기 규칙 |
| `docs/` | 번역·검수·이미지 작업 가이드 |
| `tools/` | 빌드·검사·이미지·패치 도구 |
| `fonts/` | 갈무리 글꼴 (SIL OFL 1.1) |
| `release/` | 배포 패치와 사용자 설명서 |
| `work/`, `rom/` | 원문 추출·미리보기·빌드 결과, 원본 롬 (커밋하지 않음) |

### 기술 메모

- **대사**: `2D/MessageText/*.bmg` 는 빅엔디언 BMG, 인코딩 3 = Shift-JIS. 일본어 대사에는 후리가나 태그(`1A len FF00 02 …`)가 붙어 있어 번역 시 제거합니다.
- **글꼴**: BMG마다 전용 서브셋 NFTR을 씁니다. 새 글리프의 코드는 글꼴의 **마지막 전체범위(0x0000-0xFFFF) CMAP 블록에 병합**해야 합니다. 뒤에 새 블록을 추가하면 게임이 범위가 맞는 첫 블록에서 검색을 끝내 글자가 공백으로 나옵니다.
- **글자 폭**: 게임은 CWDH의 `charWidth` 가 아니라 `left + glyphWidth` 만큼 커서를 전진시킵니다.
- **텍스처**: `*.ntfq` 는 헤더가 없어 파일 크기로 형식(COMP4x4 / PLTT4·16·256 / A5I3·A3I5)과 크기를 판정합니다(`tools/texchoice.json`). 일부 스크립트의 `RegistTexture` 크기 값은 실제와 다릅니다.
- **COMP4x4 함정**: 팔레트를 늘리면 실기에서 다른 텍스처의 색이 깨집니다. 인코더는 기존 색 묶음만 재사용해 팔레트 크기를 유지합니다.
- **조각 텍스처 함정**: 게임이 원본 글자 높이만큼 잘라 쓰는 이미지(행성 이름 등)는 한글이 그 범위를 넘으면 윗부분이 아래로 되감겨 찍힙니다. 원본 글자 행 범위에 맞춰야 합니다.
- **코드 패치**: 오버레이 4 `+0x233A8` (본체 언어 분기 → 항상 영문 자판).
- arm9은 BLZ(역방향 LZ)로 압축돼 있습니다(`tools/blz.py`).

## 크레딧·라이선스

- 한글화 작업: arqhive
- 글꼴: [갈무리 (Galmuri)](https://github.com/quiple/galmuri) © Lee Minseo — SIL Open Font License 1.1 ([`fonts/OFL.txt`](fonts/OFL.txt))
- 이 저장소의 스크립트: MIT License ([`LICENSE`](LICENSE))
- 스타폭스 커맨드는 Nintendo의 저작물입니다. 정품을 소유한 분만 이용해 주세요.

## 면책조항

- 이 패치는 팬이 비영리 목적으로 만든 **비공식** 한글 패치이며, Nintendo, Q-Games 및 관련 권리자와 아무런 관계가 없고 이들의 승인·보증을 받지 않았습니다.
- Star Fox, 스타폭스 및 관련 명칭·캐릭터·이미지의 권리는 각 권리자에게 있습니다.
- 이 저장소와 릴리즈는 게임 롬을 포함하거나 배포하지 않습니다. 패치는 이용자가 **직접 소유한 정품 게임**에서 추출한 롬에만 적용해 주세요. 롬의 불법 다운로드·공유는 허용하지 않으며, 관련 요청에는 응하지 않습니다.
- 패치된 롬을 배포하거나 판매하지 마세요. 이 패치를 유료로 판매하거나 상업적으로 이용하는 것을 금지합니다.
- 이 패치는 "있는 그대로" 제공되며, 사용으로 인해 발생하는 세이브 데이터 손실, 기기·에뮬레이터 문제 등 어떠한 손해에 대해서도 제작자는 책임지지 않습니다. 적용 전 원본 롬과 세이브 파일을 반드시 백업해 주세요.
- 권리자의 요청이 있을 경우 이 저장소와 배포물은 사전 예고 없이 삭제될 수 있습니다.
