#!/usr/bin/env python3
"""Refresh the snapshot the profile README's cards are drawn from.

Writes data/profile.json — the only data the README needs, since its stat,
language and streak cards are rendered from it by scripts/build_readme.py.

Only public, unauthenticated GitHub endpoints are used, so no token is needed:

    python3 scripts/fetch_profile.py

The daily workflow (.github/workflows/refresh-readme.yml) runs this and
build_readme.py together, then commits whatever moved.
"""

from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
import urllib.error
import urllib.request

USER = "mathewmusango"
API = "https://api.github.com"
ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = {"User-Agent": "mathewmusango-profile-readme", "Accept": "application/vnd.github+json"}


def get_bytes(url: str, accept: str = "application/vnd.github+json") -> bytes:
    headers = dict(UA)
    headers["Accept"] = accept
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as resp:
        return resp.read()


def get_json(url: str):
    return json.loads(get_bytes(url))


def get_text(url: str) -> str:
    return get_bytes(url, "text/html").decode("utf-8", "replace")


def contributions_calendar() -> dict:
    """Parse the public contribution calendar — one cell per day, contiguous."""
    html = get_text(f"https://github.com/users/{USER}/contributions")
    days = []
    for chunk in html.split("<td")[1:]:
        date = re.search(r'data-date="(\d{4}-\d{2}-\d{2})"', chunk)
        level = re.search(r'data-level="(\d+)"', chunk)
        if not (date and level):
            continue
        tooltip = re.search(r"<tool-tip[^>]*>(.*?)</tool-tip>", chunk, re.S)
        text = re.sub(r"\s+", " ", tooltip.group(1)).strip() if tooltip else ""
        found = re.match(r"([\d,]+)\s+contribution", text)
        days.append(
            {
                "date": date.group(1),
                "level": int(level.group(1)),
                "count": int(found.group(1).replace(",", "")) if found else 0,
            }
        )

    if not days:
        raise RuntimeError("no contribution cells found — GitHub markup changed?")

    days.sort(key=lambda day: day["date"])
    return {
        "start": days[0]["date"],
        "levels": "".join(str(day["level"]) for day in days),
        "counts": [day["count"] for day in days],
        "total": sum(day["count"] for day in days),
        "days": len(days),
    }


def build_snapshot() -> dict:
    user = get_json(f"{API}/users/{USER}")
    repos = [
        repo
        for repo in get_json(f"{API}/users/{USER}/repos?per_page=100&sort=pushed")
        if not repo["fork"]
    ]

    languages: dict[str, int] = {}
    for repo in repos:
        try:
            for name, size in get_json(f"{API}/repos/{USER}/{repo['name']}/languages").items():
                languages[name] = languages.get(name, 0) + size
        except urllib.error.HTTPError:
            pass

    total_bytes = sum(languages.values()) or 1
    top_languages = [
        {"name": name, "pct": round(size * 1000 / total_bytes) / 10}
        for name, size in sorted(languages.items(), key=lambda item: -item[1])
    ]

    created = dt.date.fromisoformat(user["created_at"][:10])
    today = dt.date.today()
    years_active = max(1, today.year - created.year - int(today < created.replace(year=today.year)))

    return {
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "stats": {
            "repos": len(repos),
            "stars": sum(repo["stargazers_count"] for repo in repos),
            "followers": user["followers"],
            "years_active": years_active,
        },
        "languages": top_languages,
        "contributions": contributions_calendar(),
    }


def main() -> None:
    snapshot = build_snapshot()

    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "profile.json").write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    stats = snapshot["stats"]
    contributions = snapshot["contributions"]
    print("repos {}  stars {}".format(stats["repos"], stats["stars"]))
    print("followers {}  years active {}".format(stats["followers"], stats["years_active"]))
    print(
        "languages "
        + ", ".join("{:.1f}% {}".format(lang["pct"], lang["name"]) for lang in snapshot["languages"])
    )
    print("calendar {} days, {} contributions".format(contributions["days"], contributions["total"]))


if __name__ == "__main__":
    main()
