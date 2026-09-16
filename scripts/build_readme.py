#!/usr/bin/env python3
"""Render the profile README and its cards.

GitHub only accepts plain markdown on a profile page — no CSS, no scripts — so
the dark cards in the reference design are drawn as SVG images generated here
and committed alongside the README. Nothing is fetched from a third-party card
service: every pixel comes from GitHub's public API (via fetch_profile.py) and
this file.

Writes:
  README.md                 the profile view, rendered on github.com/<user>
  assets/svg/hero.svg       banner — handle, name, tagline
  assets/svg/stats.svg      four-cell stat row
  assets/svg/tech.svg       core technologies + language bars

Run:
  python3 scripts/fetch_profile.py && python3 scripts/build_readme.py
"""

from __future__ import annotations

import datetime as dt
import html
import json
import pathlib

USER = "mathewmusango"
BRANCH = "main"
ROOT = pathlib.Path(__file__).resolve().parent.parent

# Absolute raw URLs: they resolve on the profile page, in the repo view, and
# anywhere the README is embedded. (Relative paths work in the repo view only.)
RAW = f"https://raw.githubusercontent.com/{USER}/{USER}/{BRANCH}"

BG = "#030303"
SURFACE = "#0a0a0a"
SURFACE_2 = "#111111"
BORDER = "#222222"
FG = "#ededed"
MUTED = "#8b949e"
FAINT = "#6e7681"
GREEN = "#26a641"
GREEN_BRIGHT = "#39d353"
GREEN_BTN = "#238636"

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

SITE = "https://mathewmusango.github.io/my-portfolio/"
LINKEDIN = "https://www.linkedin.com/in/mathew-musango/"
EMAIL = "musangomathew@gmail.com"

# Advance widths (em) for Helvetica-ish metrics — enough to centre and wrap
# text without pulling in a font library.
NARROW = {" ": 0.278, ".": 0.278, ",": 0.278, ":": 0.278, ";": 0.278, "'": 0.191,
          "!": 0.278, "|": 0.222, "(": 0.333, ")": 0.333, "-": 0.333, "/": 0.278}
WIDE = {"—": 1.0, "·": 0.35, "…": 0.9}


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def text_width(text: str, size: float) -> float:
    total = 0.0
    for char in text:
        if char in NARROW:
            total += NARROW[char]
        elif char in WIDE:
            total += WIDE[char]
        elif char.isdigit():
            total += 0.556
        elif char.isupper():
            total += 0.667
        elif ord(char) > 0x2000:  # emoji and friends — assume a full em
            total += 1.0
        else:
            total += 0.52
    return total * size


def compact(value: int) -> str:
    if value < 1000:
        return str(value)
    if value < 10000:
        return f"{value:,}"
    if value < 1000000:
        return f"{value / 1000:.1f}".rstrip("0").rstrip(".") + "k"
    return f"{value / 1000000:.1f}".rstrip("0").rstrip(".") + "M"


def text(content, x, y, size, fill=FG, *, anchor="start", bold=False, mono=False,
         spacing=None, opacity=None):
    attributes = [
        f'x="{x:.1f}"',
        f'y="{y:.1f}"',
        f'font-family="{MONO if mono else FONT}"',
        f'font-size="{size}"',
        f'fill="{fill}"',
    ]
    if anchor != "start":
        attributes.append(f'text-anchor="{anchor}"')
    if bold:
        attributes.append('font-weight="700"')
    if spacing:
        attributes.append(f'letter-spacing="{spacing}"')
    if opacity:
        attributes.append(f'opacity="{opacity}"')
    return f'<text {" ".join(attributes)}>{esc(content)}</text>'


def wrap(content: str, size: float, max_width: float) -> list[str]:
    lines, current = [], ""
    for word in content.split():
        candidate = f"{current} {word}".strip()
        if current and text_width(candidate, size) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def svg(width: int, height: int, body: list[str], title: str, defs: str = "") -> str:
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-label="{esc(title)}">',
            f"<title>{esc(title)}</title>",
            defs,
            *body,
            "</svg>",
            "",
        ]
    )


def card(x, y, width, height, radius=16, fill=SURFACE, stroke=BORDER):
    return (
        f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="{radius}" '
        f'fill="{fill}" stroke="{stroke}"/>'
    )


def hero(snapshot: dict) -> str:
    width, height = 1280, 300
    user = snapshot["user"]
    handle = f"GITHUB · @{user['login'].upper()}"
    heading = f"Welcome to {user['name']}'s Hub"
    tagline = user["bio"] or "Public repositories, languages and activity on GitHub."

    pill_width = text_width(handle, 13) * 1.06 + 34
    pill_x = (width - pill_width) / 2
    lines = wrap(tagline, 19, 980)
    tagline_start = 196

    body = [
        f'<rect width="{width}" height="{height}" fill="{BG}"/>',
        f'<rect width="{width}" height="{height}" fill="url(#glow)"/>',
        f'<rect x="{pill_x:.1f}" y="46" width="{pill_width:.1f}" height="32" rx="16" '
        f'fill="{SURFACE_2}" stroke="{BORDER}"/>',
        text(handle, width / 2, 67, 13, MUTED, anchor="middle", bold=True, spacing=1.6),
        text(heading, width / 2, 148, 46, FG, anchor="middle", bold=True, spacing=-1),
    ]
    for index, line in enumerate(lines[:2]):
        body.append(text(line, width / 2, tagline_start + index * 28, 19, MUTED, anchor="middle"))

    defs = (
        '<defs><radialGradient id="glow" cx="50%" cy="0%" r="72%">'
        f'<stop offset="0%" stop-color="{GREEN}" stop-opacity="0.20"/>'
        f'<stop offset="100%" stop-color="{GREEN}" stop-opacity="0"/>'
        "</radialGradient></defs>"
    )
    return svg(width, height, body, f"{user['name']} — {tagline}", defs)


def stats(snapshot: dict) -> str:
    width, height = 1280, 150
    gap, margin, card_height, card_y = 20, 20, 110, 20
    card_width = (width - margin * 2 - gap * 3) / 4

    cells = [
        (compact(snapshot["stats"]["repos"]), "Total repos"),
        (compact(snapshot["stats"]["stars"]), "All stars"),
        (compact(snapshot["stats"]["followers"]), "Followers"),
        (str(snapshot["stats"]["years_active"]), "Years active"),
    ]

    body = [f'<rect width="{width}" height="{height}" fill="{BG}"/>']
    for index, (value, label) in enumerate(cells):
        x = margin + index * (card_width + gap)
        centre = x + card_width / 2
        body.append(card(x, card_y, card_width, card_height))
        body.append(text(value, centre, card_y + 58, 38, FG, anchor="middle", bold=True))
        body.append(text(label.upper(), centre, card_y + 88, 12, MUTED, anchor="middle",
                         bold=True, spacing=1.6))
    return svg(width, height, body, " ".join(f"{v} {l.lower()}" for v, l in cells))


def tech(snapshot: dict) -> str:
    width, margin = 1280, 20
    inner_x = margin + 28
    inner_right = width - margin - 28
    inner_width = inner_right - inner_x

    chip_size, chip_height, chip_pad, chip_gap = 13, 30, 12, 8
    languages = snapshot["languages"][:6]

    # Lay the chips out first so the card height can be computed.
    chips, x, y = [], inner_x, 120
    for item in snapshot["core_tech"]:
        chip_width = text_width(item, chip_size) + chip_pad * 2
        if x + chip_width > inner_right and x > inner_x:
            x, y = inner_x, y + chip_height + chip_gap
        chips.append(
            f'<rect x="{x:.1f}" y="{y}" width="{chip_width:.1f}" height="{chip_height}" '
            f'rx="{chip_height / 2}" fill="{SURFACE_2}" stroke="{BORDER}"/>'
        )
        chips.append(text(item, x + chip_pad, y + chip_height / 2 + chip_size * 0.36,
                          chip_size, MUTED))
        x += chip_width + chip_gap

    bars_y = y + chip_height + 44
    bars, y = [], bars_y
    for language in languages:
        bars.append(text(language["name"], inner_x, y, 15, FG, bold=True))
        bars.append(text(f"{language['pct']:.1f}%", inner_right, y, 13, MUTED,
                         anchor="end", mono=True))
        bars.append(f'<rect x="{inner_x}" y="{y + 12}" width="{inner_width}" height="6" '
                    f'rx="3" fill="#1a1a1a"/>')
        filled = max(inner_width * language["pct"] / 100, 6)
        bars.append(f'<rect x="{inner_x}" y="{y + 12}" width="{filled:.1f}" height="6" '
                    f'rx="3" fill="url(#bar)"/>')
        y += 46

    height = int(y + 6)
    body = [
        f'<rect width="{width}" height="{height}" fill="{BG}"/>',
        card(margin, margin, width - margin * 2, height - margin * 2),
        text("Tech Stack & Languages", inner_x, 68, 22, FG, bold=True),
        text("By bytes committed", inner_right, 68, 14, MUTED, anchor="end"),
        text("CORE TECHNOLOGIES", inner_x, 104, 11, FAINT, bold=True, spacing=1.6),
        *chips,
        text("LANGUAGES", inner_x, bars_y - 22, 11, FAINT, bold=True, spacing=1.6),
        *bars,
    ]
    defs = (
        '<defs><linearGradient id="bar" x1="0%" y1="0%" x2="100%" y2="0%">'
        f'<stop offset="0%" stop-color="{GREEN_BTN}"/>'
        f'<stop offset="100%" stop-color="{GREEN_BRIGHT}"/>'
        "</linearGradient></defs>"
    )
    return svg(width, height, body, "Tech stack and languages", defs)


def projects_table(snapshot: dict) -> str:
    rows = [
        "| Repository | About | Stack | ★ |",
        "| :--- | :--- | :--- | ---: |",
    ]
    for project in snapshot["projects"]:
        about = (project["description"] or "—").replace("|", "\\|")
        if len(about) > 150:
            about = about[:147].rstrip() + "…"
        stack = f"`{project['language']}`" if project["language"] else "—"
        rows.append(
            f"| **[{project['name']}]({project['url']})** | {about} | {stack} | "
            f"{compact(project['stars'])} |"
        )
    return "\n".join(rows)


def readme(snapshot: dict) -> str:
    user = snapshot["user"]
    refreshed = dt.date.fromisoformat(snapshot["generated"][:10]).strftime("%d %B %Y")
    images = "\n".join(
        [
            f'<p align="center">\n  <img src="{RAW}/assets/svg/hero.svg" '
            f'alt="Welcome to {esc(user["name"])}\'s Hub" width="100%">\n</p>',
            f'<p align="center">\n  <img src="{RAW}/assets/svg/stats.svg" '
            f'alt="{snapshot["stats"]["repos"]} public repos, {snapshot["stats"]["stars"]} stars, '
            f'{snapshot["stats"]["followers"]} followers, '
            f'{snapshot["stats"]["years_active"]} years active" width="100%">\n</p>',
            f'<p align="center">\n  <img src="{RAW}/assets/svg/tech.svg" '
            f'alt="Tech stack and languages" width="100%">\n</p>',
        ]
    )

    return f"""<!-- Generated by scripts/build_readme.py — edit the script, not this file. -->

{images}

## Notable projects <sub>· most stars first</sub>

{projects_table(snapshot)}

## Elsewhere

[Portfolio]({SITE}) · [LinkedIn]({LINKEDIN}) · [Email](mailto:{EMAIL}) · [All repositories]({user['profile_url']}?tab=repositories)

<sub>Synced from GitHub's public API — last refreshed {refreshed}. Statistics, cards and this
README are generated by <a href="https://github.com/{USER}/{USER}/blob/{BRANCH}/scripts/build_readme.py">
<code>scripts/build_readme.py</code></a>; no third-party card services involved. Contribution
activity below is rendered natively by GitHub.</sub>
"""


def main() -> None:
    snapshot = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))

    svg_dir = ROOT / "assets" / "svg"
    svg_dir.mkdir(parents=True, exist_ok=True)
    (svg_dir / "hero.svg").write_text(hero(snapshot), encoding="utf-8")
    (svg_dir / "stats.svg").write_text(stats(snapshot), encoding="utf-8")
    (svg_dir / "tech.svg").write_text(tech(snapshot), encoding="utf-8")
    (ROOT / "README.md").write_text(readme(snapshot), encoding="utf-8")

    print("wrote README.md")
    for name in ("hero", "stats", "tech"):
        path = svg_dir / f"{name}.svg"
        print(f"wrote assets/svg/{name}.svg  {path.stat().st_size / 1024:.1f} KiB")


if __name__ == "__main__":
    main()
