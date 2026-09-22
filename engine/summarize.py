"""원문 기사 텍스트 → 카드뉴스 JSON. Claude API의 tool_use로 sources.py 스키마를 강제 출력합니다."""
from __future__ import annotations

import os

from anthropic import Anthropic

def _system_prompt(topic: str) -> str:
    return f"""당신은 {topic} 카드뉴스 편집자입니다. 아래 원칙을 반드시 지키세요.
- 원문에 없는 사실을 추가하지 마세요.
- 원문 문장을 그대로 옮기지 말고 재서술하세요.
- 각 기사의 출처명을 정확히 표기하세요.
- 과장하거나 클릭베이트성 표현을 쓰지 마세요.
- 존댓말, 간결한 뉴스체로 작성하세요.
- 해외 기사와 국내 기사를 함께 다루더라도 문체와 톤을 통일하세요.
- 한자를 섞어 쓰지 마세요. 고유명사를 제외하고 모든 단어는 한글로만 작성하세요 (예: "에너지發" 금지 → "에너지발"로 표기).
- headline과 title에 "A·B·C 변화"처럼 단어를 가운뎃점(·)으로 나열해 뭉뚱그리는 상투적인 AI 문구를 쓰지 마세요. 기사에서 가장 핵심적인 사실 하나를 구체적인 문장으로 표현하세요."""


DEFAULT_TOPIC = "뉴스"

EMIT_TOOL = {
    "name": "emit_cardnews",
    "description": "요약 결과를 카드뉴스 스키마에 맞춰 제출합니다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "headline": {"type": "string", "description": "표지 대표 헤드라인 (30자 이내 권장)"},
            "one_liner": {"type": "string", "description": "마무리 카드용 오늘의 한 줄 총평"},
            "items": {
                "type": "array",
                "description": "기사 순서와 동일한 개수의 카드",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "카드 제목 (30자 이내 권장)"},
                        "summary": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 3,
                            "maxItems": 3,
                            "description": "핵심 내용 3줄 (줄당 40자 이내 권장)",
                        },
                        "why": {"type": "string", "description": "이 소식이 왜 중요한지 1줄"},
                        "source": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "url": {"type": "string"},
                            },
                            "required": ["name", "url"],
                        },
                    },
                    "required": ["title", "summary", "why", "source"],
                },
            },
        },
        "required": ["headline", "one_liner", "items"],
    },
}

DEFAULT_MODEL = "claude-sonnet-5"


def generate(articles: list[dict], model: str | None = None, topic: str = DEFAULT_TOPIC) -> dict:
    """articles: [{"title", "url", "source_name", "body"}, ...] → 표준 카드뉴스 dict (date 제외)."""
    client = Anthropic()

    blocks = []
    for i, a in enumerate(articles, 1):
        blocks.append(
            f"[기사 {i}]\n제목: {a['title']}\n출처: {a['source_name']}\nURL: {a['url']}\n본문:\n{a['body']}"
        )
    user_prompt = (
        f"아래 {len(articles)}개의 기사를 각각 카드 1장 분량으로 요약해 emit_cardnews 도구로 제출하세요.\n"
        f"items 배열은 기사 순서를 그대로 유지하세요. headline과 one_liner는 전체 기사를 아우르는 내용으로 작성하세요.\n\n"
        + "\n\n".join(blocks)
    )

    resp = client.messages.create(
        model=model or os.environ.get("CLAUDE_MODEL", DEFAULT_MODEL),
        max_tokens=4096,
        system=_system_prompt(topic),
        tools=[EMIT_TOOL],
        tool_choice={"type": "tool", "name": "emit_cardnews"},
        messages=[{"role": "user", "content": user_prompt}],
    )

    for block in resp.content:
        if block.type == "tool_use" and block.name == "emit_cardnews":
            return block.input
    raise RuntimeError("Claude가 emit_cardnews 도구를 호출하지 않았습니다.")
