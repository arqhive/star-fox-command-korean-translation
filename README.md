# 스타폭스 커맨드 (NDS) 한글 패치

*Star Fox Command* (닌텐도 DS, 일본판 `ASFJ`) 비공식 한국어 팬 패치입니다.
대사는 일본어판 원문을 기준으로 번역했습니다.

**제작: arqhive** · **최신 버전: [v1.1](https://github.com/arqhive/star-fox-command-korean-translation/releases/tag/v1.1)**

- 대사 약 2,870문장 전체를 한글화했습니다(스토리, 전투 무전, 작전 화면, 오프닝·엔딩, 적 이름).
- 그림 글씨 496장을 한글화했습니다(메뉴, 타이틀, 스테이지 제목, 갤러리, 옵션, Wi-Fi 안내, 작전 화면, 캐릭터 이름표).
- 글꼴은 닌텐도 DS 글꼴 디자인을 바탕으로 한 도트 글꼴 **갈무리**를 씁니다.
- 인물·지명은 한국 정식 발매작(스타폭스 2026, 스타폭스 64 3D) 표기를 따랐습니다(안돌프, 팔코 람바디, 라일라트, 카티나).
- 닉네임 입력 화면이 영문 자판으로 시작하도록 코드를 고쳤습니다.
- 메뉴(DSi, TWiLight Menu++ 등)에 보이는 게임 이름을 "스타폭스 커맨드"로 바꿨습니다.
- **원본과 같은 32MB 롬 크기를 유지합니다.** 롬을 확장하지 않았습니다.

> 이 저장소에는 **게임 데이터(롬·디스크 이미지, 추출한 원문 대사, 그래픽, 스크린샷)가 들어 있지 않습니다.**
> 패치를 만들거나 적용하려면 본인이 소유한 게임에서 직접 덤프한 원본이 필요합니다.

## 사용자용: 패치 적용

### 준비물

- 일본판 롬(`ASFJ`). 북미·유럽판에는 적용할 수 없고, 이전 버전 패치를 적용한 롬에 덧씌울 수도 없습니다.
- BPS 패치 도구. [Rom Patcher JS](https://www.marcrobledo.com/RomPatcher.js/)나 Floating IPS, 또는 이 저장소의 `tools/bps.py`를 쓰면 됩니다.

### 적용 방법

1. [배포 페이지](https://github.com/arqhive/star-fox-command-korean-translation/releases/tag/v1.1)에서 `StarFoxCommand_KO_v1.1.bps`를 받습니다.
2. 원본 일본판 롬에 패치를 적용합니다.
3. 결과 롬의 확인값을 아래 표와 비교합니다.

자세한 방법은 [`README_한국어.txt`](release/README_한국어.txt)를 참고하세요.

### 파일 확인값

| 항목 | 원본 일본판 | 패치 적용 결과 (v1.1) |
|---|---|---|
| 크기 | 33,554,432 바이트 | 33,554,432 바이트 |
| CRC32 | `618C4089` | `2182FDE4` |
| MD5 | `81d9550164d4c0a3756d1271ee063a1a` | `f0ccbdde83e8e17d0235be4304a8029c` |
| SHA-1 | `fe0a3ba974132de5d63429b48ee9d3e8b6d6a318` | `0678aca6a45164a555b1c14f35faa0cedd1f0c45` |

원본 파일명 예: `Star Fox Command (Japan).nds`

### 실행 환경

- **확인함**: melonDS, 3DS + TWiLight Menu++.

### 알려진 문제

- 칸 높이가 7에서 9픽셀인 작은 이름 목록 일부는 받침이 많은 글자가 뭉개져 보일 수 있습니다.
- 여러 조각을 조합해 보여 주는 이미지(라운드 정보 등)는 화면에 따라 어색할 수 있습니다.
- 닉네임은 영문·기호만 입력할 수 있습니다. 한글 입력은 지원하지 않습니다.
- 게임에서 쓰이지 않는 것으로 보이는 옛 대사 파일(`corneria.bmg`)은 번역하지 않았습니다.

이상한 화면이나 어색한 문장을 발견하면 이슈로 알려 주세요.

## 개발자용: 직접 빌드

### 요구 사항

- Python 3.10 이상, [Pillow](https://pypi.org/project/pillow/), [NumPy](https://pypi.org/project/numpy/).
- 원본 일본판 롬(위 확인값과 일치하는 파일).
- 글꼴은 저장소의 [`fonts/`](fonts/)(갈무리 TTF)를 쓰므로 OS 폰트와 관계없이 같은 결과가 나옵니다.

```bash
pip install pillow numpy
```

### 빌드

원본 롬을 `rom/Star Fox Command (Japan).nds`에 두거나 환경 변수 `SFC_JP_ROM`으로 경로를 지정한 뒤 실행합니다.

```bash
python tools/build.py
python tools/bps.py create "rom/Star Fox Command (Japan).nds" "work/Star Fox Command (Japan) [KO].nds" release/StarFoxCommand_KO_v1.1.bps
```

결과는 `work/Star Fox Command (Japan) [KO].nds`에 만들어지며, v1.1 배포본과 바이트 단위로 같습니다.

`build.py`는 다음을 수행합니다.

1. `translation/ko/*.json`의 한국어 대사를 BMG(`2D/MessageText/*.bmg`)에 다시 기록합니다. 쓰이지 않게 된 옛 일본어 문자열은 버리고 문자열 영역을 새로 구성합니다.
2. 번역에 쓰인 한글 음절을 사용하지 않는 Shift-JIS 코드에 배정하고, 파일별 서브셋 글꼴(NFTR)에 갈무리 글리프를 추가합니다.
3. `translation/images/**/*.json` 명세대로 텍스처(`3D/Textures/**/*.ntfq`)와 2D 타일 그림(`2D/**/*.nbfc`)의 일본어를 지우고 한글을 그려 원래 형식으로 다시 인코딩합니다.
4. 오버레이 4의 분기 2바이트를 고쳐 닉네임 자판 기본 모드를 영문으로 바꾸고, 배너(메뉴에 보이는 게임 이름)의 6개 언어 칸을 한국어로 바꾼 뒤 배너 CRC16을 갱신합니다.
5. 파일을 제자리에 넣거나, 들어가지 않으면 롬 끝에 배치하고 FAT·사용 크기·헤더 체크섬을 갱신합니다.

### 번역 수정

```bash
python tools/export_src.py          # work/src/*.json 에 일본어 원문 추출 (원문이므로 커밋 금지)
python tools/check_ko.py scenario_1 # 줄 수·화면 폭·@1 치환기호·일본어 잔여 검사
```

- 대사: [`translation/ko/*.json`](translation/ko). `{"메시지 번호": "번역문"}` 형식이며 줄바꿈은 `\n`, `@1`은 플레이어 이름 치환기호입니다.
- 묶음은 `scenario_1`에서 `scenario_4`까지(스토리), `battle_1`·`battle_2`(전투 무전·튜토리얼), `strategy_1`·`strategy_2`(작전 화면), `advertise_enemy`(오프닝·엔딩, 적 이름)입니다.
- 용어·말투: [`translation/GLOSSARY.md`](translation/GLOSSARY.md).
- 문장 부호·문체 검수 기준: [`docs/PUNCT_GUIDE.md`](docs/PUNCT_GUIDE.md), [`docs/COMMA_GUIDE.md`](docs/COMMA_GUIDE.md), [`docs/NATURAL_GUIDE.md`](docs/NATURAL_GUIDE.md).

### 그림 글씨 수정

```bash
python tools/imgtool.py info   Menu/General/menu_all   # 형식·크기·팔레트 출력 + 확대 격자 이미지
python tools/imgtool.py render Menu/General/menu_all   # 명세 적용 → 게임 형식 변환 → 결과 미리보기
```

- 명세: [`translation/images/**/*.json`](translation/images). 이미지마다 지울 영역(`clear`/`fill`/`hfill`/`copy`)과 넣을 글자(`text`: 글꼴·크기·색·외곽선·정렬)를 정의합니다.
- 작성 방법: [`docs/IMAGE_GUIDE.md`](docs/IMAGE_GUIDE.md).
- 결과 미리보기는 `work/img/`에 저장됩니다. 커밋하지 않습니다.

### 폴더 구조

```
translation/ko/        한국어 대사(BMG 메시지 번호와 문장)
translation/images/    이미지별 편집 명세
translation/GLOSSARY.md  용어집·말투·표기 규칙
docs/                  번역·검수·이미지 작업 가이드, 릴리즈 노트 사본(docs/releases/)
tools/                 빌드·검사·이미지·패치 도구
fonts/                 갈무리 글꼴과 라이선스(SIL OFL 1.1)
release/               배포 패치와 사용자 설명서
work/, rom/            원문 추출·미리보기·빌드 결과, 원본 롬(커밋하지 않음)
```

### 기술 문서

- **대사**: `2D/MessageText/*.bmg`는 빅엔디언 BMG이고 인코딩 3(Shift-JIS)을 씁니다. 일본어 대사에는 후리가나 태그(`1A len FF00 02 …`)가 붙어 있어 번역할 때 제거합니다.
- **글꼴**: BMG마다 전용 서브셋 NFTR을 씁니다. 새 글리프의 코드는 글꼴의 **마지막 전체 범위(0x0000-0xFFFF) CMAP 블록에 병합**해야 합니다. 뒤에 새 블록을 추가하면 게임이 범위가 맞는 첫 블록에서 검색을 끝내 글자가 공백으로 나옵니다.
- **글자 폭**: 게임은 CWDH의 `charWidth`가 아니라 `left + glyphWidth`만큼 커서를 전진시킵니다.
- **텍스처**: `*.ntfq`는 헤더가 없어 파일 크기로 형식(COMP4x4, PLTT4·16·256, A5I3·A3I5)과 크기를 판정합니다(`tools/texchoice.json`). 일부 스크립트의 `RegistTexture` 크기 값은 실제와 다릅니다.
- **COMP4x4 함정**: 팔레트를 늘리면 실기에서 다른 텍스처의 색이 깨집니다. 인코더는 기존 색 묶음만 재사용해 팔레트 크기를 유지합니다.
- **조각 텍스처 함정**: 게임이 원본 글자 높이만큼 잘라 쓰는 이미지(행성 이름 등)는 한글이 그 범위를 넘으면 윗부분이 아래로 되감겨 찍힙니다. 원본 글자 행 범위에 맞춰야 합니다.
- **코드 패치**: 오버레이 4 `+0x233A8`의 본체 언어 분기를 고쳐 항상 영문 자판이 뜨게 했습니다.
- arm9은 BLZ(역방향 LZ)로 압축돼 있습니다(`tools/blz.py`).

## 변경 내역

전체 내역은 [`CHANGELOG.md`](CHANGELOG.md)에 있습니다.

## 크레딧·라이선스

- 이 저장소의 도구 코드, 한국어 번역문, 문서: [MIT License](LICENSE) (© 2026 arqhive).
- 글꼴: [갈무리(Galmuri)](https://github.com/quiple/galmuri) © Lee Minseo, [SIL Open Font License 1.1](fonts/OFL.txt).

## 면책

비공식 팬 번역이며 Nintendo와 관련이 없습니다. 「스타폭스 커맨드」 관련 상표·저작권은 Nintendo에 있습니다.
패치를 적용한 게임 파일의 배포를 금지합니다.
