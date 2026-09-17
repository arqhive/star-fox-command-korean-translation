# 이미지 한글화 작업 가이드 (스타 폭스 커맨드 NDS, 일본판 기반)

작업 폴더: `C:\Users\hgyst\Claude Work\스타 폭스 커맨드\tools`
Bash에서는 항상 `export PYTHONIOENCODING=utf-8; cd "/c/Users/hgyst/Claude Work/스타 폭스 커맨드/tools"` 후 실행.

## 목표
일본어 글자가 들어간 게임 이미지(텍스처/2D 그림)를 한국어로 바꾼다. 결과물은 이미지마다 **편집 명세 JSON** 한 개:
`translation/images/<경로>.json` (예: `translation/images/Menu/Option/option_txt.json`, `translation/images/2D/Pause/pause_wnd.json`)
빌드는 하지 않는다(메인 세션이 한다). 다른 담당의 파일이나 스크립트(.py)는 수정하지 않는다.

## 도구
- `python tools/imgtool.py info <경로>` : 형식·크기·팔레트 출력, `work/img/<경로>_grid.png`(확대 + 8px 빨간 격자, 32px 노란 격자·좌표 숫자) 생성, 북미판 영어 버전이 있으면 `work/img/<경로>_us.png`(2배) 생성 → **Read 도구로 이미지를 직접 보고** 좌표를 잡는다. 격자 이미지 배율은 출력에 표시됨(보통 4배: 이미지 픽셀 = 원본좌표×4).
- `python tools/imgtool.py render <경로>` : 명세를 적용해 게임 형식으로 변환→다시 디코드한 결과를 `work/img/<경로>_preview.png`(위 원본 / 아래 결과)로 저장 → Read로 확인하고 만족할 때까지 명세를 고친다.

## 명세(JSON) 연산 — 좌표는 원본 픽셀 기준 [x, y, w, h]
```json
{"edits": [
  {"op": "clear", "rect": [x,y,w,h]},                         // 투명으로 지움 (배경이 투명한 글자 이미지)
  {"op": "fill",  "rect": [x,y,w,h], "color": "#rrggbb"},     // 단색
  {"op": "hfill", "rect": [x,y,w,h], "from_x": x0},           // 각 행을 원본 x0 열 색으로 채움 (세로 그라데이션 띠/버튼 배경 복원)
  {"op": "vfill", "rect": [x,y,w,h], "from_y": y0},           // 각 열을 원본 y0 행 색으로 채움 (가로 그라데이션 배경)
  {"op": "copy",  "src": [x,y,w,h], "dst": [x,y]},            // 원본의 다른 영역을 복사 (무늬 있는 배경 복원)
  {"op": "text",  "text": "싱글 플레이", "rect": [x,y,w,h],
     "font": "malgunbd", "size": 12, "bold": 1,
     "color": "#ffffff", "color2": "#aaaaaa",                 // color2: 세로 그라데이션(선택)
     "outline": "#000000", "outline_w": 1,                    // 외곽선(선택)
     "shadow": [1, 1, "#000000"],                             // 그림자(선택)
     "align": "center", "valign": "middle", "line_gap": 0, "spacing": 0, "aa": true,
     "scale_y": 1.0}                                           // 세로 배율(선택): 세로로 눌린 텍스처는 0.5 등
]}
```
- 연산은 순서대로 적용되며 copy/hfill/vfill은 항상 **원본** 픽셀을 읽는다.
- text는 rect 안에 정렬되고, 폭이 넘치면 자동으로 가로 압축된다(너무 압축되면 size를 줄이거나 줄바꿈 `\n`).
- 글꼴: `malgunbd`(맑은 고딕 굵게, 기본) / `malgun` / `gulim`(작은 글자에 선명, aa:false 권장) / `batang`.
- 결과는 원본 팔레트 색으로 강제 변환되므로 **색은 `info`가 출력한 팔레트 색이나 원본 글자 색**을 쓴다. COMP4x4 형식은 색 제한이 느슨하다.

## 품질 기준
1. 일본어 글자(후리가나 포함)는 흔적 없이 지운다. 배경이 무늬/그라데이션이면 hfill/vfill/copy로 자연스럽게 복원한다.
2. 한글 크기·굵기·색·외곽선·그림자·정렬을 원본 일본어 글자와 최대한 비슷하게 맞춘다(원본 글자 높이 ≈ size, 보통 bold:1). 너무 작아 읽기 어려우면 안 된다(최소 size 10 정도, 아주 작은 글자는 gulim + aa:false).
3. 글자 이외의 그림(캐릭터, 아이콘, 테두리, 숫자, 영문 로고)은 건드리지 않는다. 영문·숫자만 있는 이미지는 명세를 만들지 않는다.
4. 한 이미지에 같은 문구가 여러 상태(일반/선택/눌림 등 색만 다른 복사본)로 있으면 **모두** 바꾼다.
5. 번역은 `translation/GLOSSARY.md`(인물·지명·용어·"이미지(UI) 용어" 섹션)를 따른다. 뜻은 일본어 원문 기준, 북미판 이미지는 의미 참고용.
6. 반드시 render 결과를 눈으로 확인한다(글자 잘림, 배경 얼룩, 남은 일본어, 색 깨짐 확인).
7. 격자 이미지가 줄무늬/어긋나 보이는 등 **디코드 자체가 깨진 것**으로 보이면 작업하지 말고 보고서에 적는다.

## 보고서(한국어, 짧게)
- 처리한 이미지 수 / 명세를 만들지 않은 이미지와 이유(일본어 없음 등)
- 디코드가 깨져 보인 이미지
- 용어집에 없어서 정한 번역(일본어 → 한국어)
