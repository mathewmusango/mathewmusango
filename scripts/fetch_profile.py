#!/usr/bin/env python3
"""Refresh the snapshot the profile README's cards are drawn from.

Writes data/profile.json — the only data the README needs, since its stat,
language and streak cards are rendered from it by scripts/build_readme.py.

Works with or without a token:

    python3 scripts/fetch_profile.py                        # public data only
    GITHUB_TOKEN=<token> python3 scripts/fetch_profile.py   # + private repos

With a token (and REPO_SCOPE = "all", the default) the repository count, star
total and language mix cover **public and private** repositories; set
REPO_SCOPE = "public" to keep it public-only even when a token is present.
Without a token — or if one is rejected, which is warned about and never fatal —
it falls back to public data. The workflow passes PROFILE_TOKEN when it is set.

Private *contributions* are not something this script can switch on: they are a
GitHub profile setting. Turn on "Include private contributions on my profile"
and the calendar read here (and GitHub's own graph) will include them.
"""

from __future__ import annotations

import datetime as dt
import json
import os
import pathlib
import re
import urllib.error
import urllib.request

USER = "mathewmusango"
API = "https://api.github.com"
ROOT = pathlib.Path(__file__).resolve().parent.parent
UA = {"User-Agent": "mathewmusango-profile-readme", "Accept": "application/vnd.github+json"}

# "all" = public + private repositories (needs a token); "public" = public only.
REPO_SCOPE = "all"

# Optional token with read access to your repositories. Unset = public data only.
# Anything read here comes from a public API surface, so read-only is enough.
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or ""


def get_bytes(url: str, accept: str = "application/vnd.github+json") -> bytes:
    headers = dict(UA)
    headers["Accept"] = accept
    if TOKEN:
        headers["Authorization"] = "Bearer " + TOKEN
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


def check_token() -> None:
    """Drop a token the API rejects, so a stale secret degrades instead of failing."""
    global TOKEN
    if not TOKEN:
        return
    try:
        get_json(f"{API}/user")
    except urllib.error.HTTPError as error:
        print(f"warning: token rejected ({error.code}) — continuing with public data")
        TOKEN = ""


def build_snapshot() -> dict:
    check_token()

    # With a token the repository list covers private repos too; the star total
    # and language mix follow the same list, so they are consistent with the count.
    sees_private = bool(TOKEN) and REPO_SCOPE == "all"
    repos_url = (
        f"{API}/user/repos?visibility=all&affiliation=owner&per_page=100&sort=pushed"
        if sees_private
        else f"{API}/users/{USER}/repos?per_page=100&sort=pushed"
    )

    user = get_json(f"{API}/users/{USER}")
    repos = [repo for repo in get_json(repos_url) if not repo["fork"]]
    private_repos = sum(1 for repo in repos if repo.get("private"))

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
            "scope": "all" if sees_private else "public",
            "private_repos": private_repos,
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
    scope = "public + private" if stats["scope"] == "all" else "public only"
    print(
        "repos {} ({} private)  stars {}  [scope: {}]".format(
            stats["repos"], stats["private_repos"], stats["stars"], scope
        )
    )
    print("followers {}  years active {}".format(stats["followers"], stats["years_active"]))
    print(
        "languages "
        + ", ".join("{:.1f}% {}".format(lang["pct"], lang["name"]) for lang in snapshot["languages"])
    )
    print("calendar {} days, {} contributions".format(contributions["days"], contributions["total"]))


if __name__ == "__main__":
    main()
