#!/usr/bin/env python3
"""Refresh the profile hub's data from GitHub's public endpoints.

Writes:
  data/profile.json      the snapshot, for tooling and diffs
  data/profile.js        the same snapshot as `window.PROFILE = {...}`, loaded
                         by <script src> so the page renders straight off the
                         filesystem — no `fetch`, no CORS, no runtime request
  assets/img/avatar.png  the avatar, downloaded once so the page makes no
                         third-party request when a visitor opens it

Only public, unauthenticated endpoints are used, so no token is required.
Re-run after GitHub activity you want reflected:

    python3 scripts/fetch_profile.py
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
UA = {"User-Agent": "mathewmusango-profile-hub", "Accept": "application/vnd.github+json"}

# Editorial values the GitHub API does not carry live in committed files, so
# they can change without an API round trip (build_readme.py reads them too).
CORE_TECH_FILE = ROOT / "data" / "core_tech.json"
# Shown as the "Company" row of the profile card; empty hides the row.
COMPANY = ""

MAX_PROJECTS = 8


def core_tech() -> list[str]:
    return json.loads(CORE_TECH_FILE.read_text(encoding="utf-8"))


def get_bytes(url: str, accept: str = "application/vnd.github+json") -> bytes:
    headers = dict(UA)
    headers["Accept"] = accept
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as resp:
        return resp.read()


def get_json(url: str):
    return json.loads(get_bytes(url))


def get_text(url: str, accept: str = "text/html") -> str:
    return get_bytes(url, accept).decode("utf-8", "replace")


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


def readme_first_line(repo: str) -> str:
    """Fallback description: the first prose line of the repo's README."""
    try:
        readme = get_text(f"{API}/repos/{USER}/{repo}/readme", "application/vnd.github.raw")
    except (urllib.error.HTTPError, urllib.error.URLError):
        return ""
    for line in readme.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "!", "[", "<", "|", "---", "```")):
            continue
        line = re.sub(r"[*_`\[\]]", "", line).strip()
        if line:
            return line[:200]
    return ""


def download_avatar(img_dir: pathlib.Path) -> str:
    """Download the avatar beside the page; return its site-relative path.

    GitHub's avatar endpoint may answer with PNG or JPEG depending on what it
    has cached, so the extension is taken from the bytes rather than assumed.
    """
    raw = get_bytes(f"https://github.com/{USER}.png?size=200")
    if raw.startswith(b"\x89PNG\r\n\x1a\n"):
        extension = ".png"
    elif raw.startswith(b"\xff\xd8"):
        extension = ".jpg"
    else:
        raise RuntimeError("avatar is neither PNG nor JPEG")

    img_dir.mkdir(parents=True, exist_ok=True)
    for stale in ("avatar.png", "avatar.jpg"):
        (img_dir / stale).unlink(missing_ok=True)
    name = "avatar" + extension
    (img_dir / name).write_bytes(raw)
    return "assets/img/" + name


def build_snapshot() -> dict:
    user = get_json(f"{API}/users/{USER}")
    repos = [
        repo
        for repo in get_json(f"{API}/users/{USER}/repos?per_page=100&sort=pushed")
        if not repo["fork"]
    ]

    languages: dict[str, int] = {}
    projects = []
    for repo in repos:
        try:
            for name, size in get_json(f"{API}/repos/{USER}/{repo['name']}/languages").items():
                languages[name] = languages.get(name, 0) + size
        except urllib.error.HTTPError:
            pass
        projects.append(
            {
                "name": repo["name"],
                "url": repo["html_url"],
                "description": repo["description"] or readme_first_line(repo["name"]),
                "language": repo["language"] or "",
                "stars": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "issues": repo["open_issues_count"],
                "homepage": repo["homepage"] or "",
                "pushed_at": repo["pushed_at"],
            }
        )

    projects.sort(key=lambda project: (-project["stars"], project["name"]))
    projects = projects[:MAX_PROJECTS]

    total_bytes = sum(languages.values()) or 1
    top_languages = [
        {"name": name, "pct": round(size * 100 / total_bytes, 1)}
        for name, size in sorted(languages.items(), key=lambda item: -item[1])
    ]

    created = dt.date.fromisoformat(user["created_at"][:10])
    today = dt.date.today()
    years_active = max(1, today.year - created.year - int(today < created.replace(year=today.year)))
    avatar = download_avatar(ROOT / "assets" / "img")

    return {
        "generated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "user": {
            "login": user["login"],
            "name": user["name"] or user["login"],
            "bio": user["bio"] or "",
            "company": user["company"] or COMPANY,
            "location": user["location"] or "",
            "blog": user["blog"] or "",
            "avatar": avatar,
            "profile_url": user["html_url"],
            "joined": user["created_at"][:10],
            "followers": user["followers"],
            "following": user["following"],
        },
        "stats": {
            "repos": len(repos),
            "stars": sum(repo["stargazers_count"] for repo in repos),
            "followers": user["followers"],
            "years_active": years_active,
        },
        "languages": top_languages,
        "core_tech": core_tech(),
        "projects": projects,
        "contributions": contributions_calendar(),
    }


def main() -> None:
    snapshot = build_snapshot()

    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "profile.json").write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (data_dir / "profile.js").write_text(
        "// Generated by scripts/fetch_profile.py — do not edit by hand.\n"
        "window.PROFILE = "
        + json.dumps(snapshot, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )

    stats = snapshot["stats"]
    contributions = snapshot["contributions"]
    langs = ", ".join("{} {:.1f}%".format(lang["name"], lang["pct"]) for lang in snapshot["languages"][:6])
    print("user         {} (@{})".format(snapshot["user"]["name"], snapshot["user"]["login"]))
    print("repos        {}  stars {}".format(stats["repos"], stats["stars"]))
    print("followers    {}  years active {}".format(stats["followers"], stats["years_active"]))
    print("languages    " + langs)
    print("projects     {}".format(len(snapshot["projects"])))
    print(
        "calendar     {} days, {} contributions in the last year".format(
            contributions["days"], contributions["total"]
        )
    )


if __name__ == "__main__":
    main()
