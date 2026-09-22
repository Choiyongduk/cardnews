"""카드뉴스 PNG를 별도 public 저장소(cardnews-assets)에 올려 공개 URL을 얻습니다.
Instagram Graph API는 image_url이 공개 HTTPS 주소여야만 이미지를 가져갈 수 있어서 필요합니다.
"""
from __future__ import annotations

import base64
import os
from pathlib import Path

import requests

ASSETS_REPO = "Choiyongduk/cardnews-assets"
API = "https://api.github.com"


def _token() -> str:
    token = os.environ.get("ASSETS_REPO_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise ValueError("ASSETS_REPO_TOKEN(또는 GITHUB_TOKEN)이 설정되어 있지 않습니다.")
    return token


def upload_images(pngs: list[Path], slug: str, date: str) -> list[str]:
    """pngs를 cardnews-assets/<slug>/<date>/<파일명> 경로로 올리고,
    raw.githubusercontent.com 공개 URL 목록을 같은 순서로 반환합니다."""
    headers = {
        "Authorization": f"Bearer {_token()}",
        "Accept": "application/vnd.github+json",
    }
    urls = []
    for p in pngs:
        repo_path = f"{slug}/{date}/{p.name}"
        content_b64 = base64.b64encode(p.read_bytes()).decode()
        resp = requests.put(
            f"{API}/repos/{ASSETS_REPO}/contents/{repo_path}",
            headers=headers,
            json={"message": f"add {repo_path}", "content": content_b64},
            timeout=30,
        )
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"이미지 업로드 실패({repo_path}): {resp.status_code} {resp.text}")
        urls.append(f"https://raw.githubusercontent.com/{ASSETS_REPO}/main/{repo_path}")
    return urls
