# 카드뉴스 자동 생성기

## 설치 (PowerShell, 최초 1회)
```powershell
cd <이 폴더 경로>
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m playwright install chromium
```
`Activate.ps1` 실행이 막히면 먼저 아래를 한 번 실행하세요.
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## 실행
```powershell
python render.py --channel ai-news
```
결과: `output/ai-news/<오늘날짜>/` 에 PNG 6장 + caption.txt

## 수정 포인트
| 바꾸고 싶은 것 | 파일 |
|---|---|
| 뉴스 내용 | data/sample.json |
| 채널명, 계정명, 해시태그, 카드 수 | channels/ai-news.yaml |
| 색상, 글자 크기, 여백 | templates/ai-news/style.css 상단 :root 변수 |
| 카드 레이아웃 | templates/ai-news/*.html |

## 새 채널 추가
1. `channels/ai-news.yaml` 복사 → `channels/<새이름>.yaml`, slug·name·template 수정
2. `templates/ai-news/` 복사 → `templates/<새이름>/`, style.css 색상 수정
3. `python render.py --channel <새이름>`
