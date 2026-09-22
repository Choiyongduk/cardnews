# 카드뉴스 자동 생성 엔진

## 목적
주제별 채널을 설정 파일로 교체할 수 있는 인스타그램 카드뉴스 자동 생성 엔진.
- 첫 채널: `ai-news` (AI 뉴스 요약)
- 추후: 뷰티 아카데미 홍보 채널 등 추가 예정 (yaml 1개 + 템플릿 폴더 1개로 추가)

## 구조
- `engine/` 공통 로직 — config(채널 로딩), sources(입력 소스), validate(검증), renderer(HTML→PNG), caption(캡션)
- `channels/<slug>.yaml` 채널 설정 (이름, 템플릿, 카드 수, 소스, 해시태그, 길이 기준)
- `templates/<template>/` 디자인 (base/cover/news/outro.html + style.css, 색상·크기는 CSS 변수)
- `assets/fonts/` Pretendard (OFL)
- `data/sample.json` 샘플 입력 = 소스 출력 스키마 (engine/sources.py 상단 docstring 참고)
- `output/<slug>/<날짜>/` 결과 PNG, caption.txt, html/(디버깅용)

## 실행
python render.py --channel ai-news [--date YYYY-MM-DD]

## 환경
Windows, PowerShell, VS Code, Python 3. 가상환경 `.venv` 사용.

## 규칙
- API 키 등 비밀값은 `.env`에만 저장. `.env`, `output/`은 git 제외.
- 단계별로 진행: 각 단계 시작 전 계획을 보여주고 승인 후 구현.
- 코드 변경 후 반드시 render.py를 실행해 결과를 확인하고 보고.
- 소스 출력 스키마(sample.json 형식)는 모든 소스·채널 공통. 변경 시 validate.py와 템플릿도 함께 수정.
- 요약 원칙(2단계 이후): 원문에 없는 사실 추가 금지, 원문 문장 그대로 옮기지 말고 재서술, 출처명 표기, 기사 원본 이미지 사용 금지.

## 로드맵
- [x] 1단계: 템플릿 렌더링 (JSON → HTML → PNG 6장 + caption.txt), 텍스트 넘침 자동 축소
- [ ] 2단계: Claude API로 기사 텍스트 → 카드 JSON 생성 (sources.py에 스키마 출력 강제)
- [ ] 3단계: RSS 수집, 중복 제거, 본문 추출 (RssSource 구현)
- [ ] 4단계: GitHub Actions 매일 자동 실행
- [ ] 5단계: 텔레그램 봇 미리보기 + [게시]/[건너뛰기] 승인
- [ ] 6단계: Instagram Graph API 자동 게시, 토큰 자동 갱신, 실패 알림
