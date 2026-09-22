"""날짜 기반 컬러 팔레트 로테이션. 네오브루탈리즘 톤을 유지하면서 매일 다른 조합을 보여주되,
같은 날짜를 다시 렌더링하면 항상 같은 배색이 나오도록 결정적으로 고릅니다.
팔레트는 미리 조화롭게 큐레이션한 세트만 사용합니다(무작위 생성 아님).

각 팔레트의 역할:
- yellow: 밝은 액센트 (표지 배경, 블랙 텍스트)
- violet: 어두운 액센트 (마무리 배경, 화이트 텍스트)
- pink: 어두운 액센트 (뉴스 카드 기본 포인트, 화이트 텍스트)
"""
from __future__ import annotations

import datetime as dt

PALETTES: list[dict[str, str]] = [
    {"yellow": "#F5FF3D", "pink": "#FF3B7F", "violet": "#7A5CFF"},  # 옐로우 · 핑크 · 바이올렛
    {"yellow": "#3DFFC0", "pink": "#FF6B4A", "violet": "#2E2A8F"},  # 민트 · 코랄 · 인디고
    {"yellow": "#4FD6FF", "pink": "#FF2E7A", "violet": "#6D28D9"},  # 스카이 · 핫핑크 · 퍼플
]


def pick_palette(date: dt.date) -> dict[str, str]:
    return PALETTES[date.toordinal() % len(PALETTES)]
