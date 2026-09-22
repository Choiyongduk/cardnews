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
claude 소스는 Claude API(emit_cardnews 도구)로 이 스키마 그대로 출력합니다.
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


class ClaudeArticleSource(Source):
    """2단계: 원문 기사 목록을 Claude API로 요약해 카드 JSON을 생성합니다.

    입력 파일(JSON) 스키마:
    [{"title": str, "url": str, "source_name": str, "body": str}, ...]
    """

    def load(self) -> dict:
        if "path" not in self.cfg:
            raise ValueError("claude 소스는 channels/<slug>.yaml의 source.path에 원문 기사 JSON 경로가 필요합니다.")
        path = ROOT / self.cfg["path"]
        with path.open(encoding="utf-8") as f:
            articles = json.load(f)
        from .summarize import generate

        data = generate(articles, model=self.cfg.get("model"), topic=self.cfg.get("topic", "뉴스"))
        data.setdefault("date", None)
        return data


class RssSource(Source):
    """3단계: RSS 수집 → 중복/사용 이력 제거 → 본문 추출 → Claude 요약.

    채널 설정 예:
    source:
      type: rss
      feeds:
        - https://example.com/feed.xml
      # model: claude-sonnet-5
    """

    def load(self) -> dict:
        from . import rss
        from .summarize import generate

        feeds = self.cfg.get("feeds") or []
        if not feeds:
            raise ValueError("rss 소스는 channels/<slug>.yaml의 source.feeds에 피드 URL이 최소 1개 필요합니다.")

        slug = self.cfg.get("slug", "default")
        need = self.cfg.get("cards", 4)

        candidates = rss.fetch_entries(feeds)
        already_seen = set(rss.load_seen(slug))
        candidates = [c for c in candidates if c["url"] not in already_seen]

        articles: list[dict] = []
        used_urls: list[str] = []
        for c in candidates:
            if len(articles) >= need:
                break
            body = rss.extract_body(c["url"])
            if not body:
                continue
            articles.append(
                {"title": c["title"], "url": c["url"], "source_name": c["source_name"], "body": body}
            )
            used_urls.append(c["url"])

        if len(articles) < need:
            raise ValueError(
                f"본문 추출에 성공한 새 기사가 {len(articles)}건뿐입니다 (필요: {need}건). "
                "피드를 추가하거나 잠시 후 다시 시도하세요."
            )

        data = generate(articles, model=self.cfg.get("model"), topic=self.cfg.get("topic", "뉴스"))
        data.setdefault("date", None)

        rss.save_seen(slug, list(already_seen) + used_urls)
        return data


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
    "claude": ClaudeArticleSource,
    "rss": RssSource,
    "sheet": SheetSource,
    "folder": FolderSource,
}


def get_source(source_cfg: dict) -> Source:
    kind = source_cfg.get("type", "sample")
    if kind not in REGISTRY:
        raise ValueError(f"알 수 없는 소스 타입: {kind} (가능: {', '.join(REGISTRY)})")
    return REGISTRY[kind](source_cfg)
