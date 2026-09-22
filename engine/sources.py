"""소스 입력부. 채널 설정의 source.type에 따라 교체됩니다.

모든 소스는 load()가 아래 스키마의 dict를 반환해야 합니다 (data/sample.json 참고).
{
  "date": "YYYY-MM-DD" | null,       # null이면 오늘 날짜
  "headline": str,                   # 표지 대표 헤드라인
  "one_liner": str,                  # 마무리 카드 한 줄 요약
  "items": [
    {
      "title": str,                  # 30자 이내
      "summary": [str, str, str],    # 줄당 40자 이내
      "why": str,                    # 왜 중요한가 1줄
      "source": {"name": str, "url": str}
    }
  ]
}
2단계에서 Claude API가 이 스키마 그대로 출력하게 됩니다.
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path

from .config import ROOT


class Source(ABC):
    def __init__(self, cfg: dict):
        self.cfg = cfg

    @abstractmethod
    def load(self) -> dict: ...


class SampleJsonSource(Source):
    """로컬 JSON 파일을 그대로 읽습니다 (1단계)."""

    def load(self) -> dict:
        path = ROOT / self.cfg.get("path", "data/sample.json")
        with path.open(encoding="utf-8") as f:
            return json.load(f)


class RssSource(Source):
    """3단계: RSS 수집 → 본문 추출 → Claude 요약."""

    def load(self) -> dict:
        raise NotImplementedError("RSS 소스는 3단계에서 구현합니다.")


class SheetSource(Source):
    """추후: 구글 시트(공지·일정 등) 입력."""

    def load(self) -> dict:
        raise NotImplementedError("sheet 소스는 아직 구현되지 않았습니다.")


class FolderSource(Source):
    """추후: 사진·텍스트 폴더 입력."""

    def load(self) -> dict:
        raise NotImplementedError("folder 소스는 아직 구현되지 않았습니다.")


REGISTRY: dict[str, type[Source]] = {
    "sample": SampleJsonSource,
    "rss": RssSource,
    "sheet": SheetSource,
    "folder": FolderSource,
}


def get_source(source_cfg: dict) -> Source:
    kind = source_cfg.get("type", "sample")
    if kind not in REGISTRY:
        raise ValueError(f"알 수 없는 소스 타입: {kind} (가능: {', '.join(REGISTRY)})")
    return REGISTRY[kind](source_cfg)
