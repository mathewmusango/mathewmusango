#!/usr/bin/env python3
"""Render the profile README and its cards.

GitHub accepts plain markdown and a sanitised subset of HTML on a profile page —
no CSS, no scripts — so the statistics cards are SVG images drawn here and
committed, and the contact badges come from shields.io (static badges only: no
third-party integration to go stale).

Writes:
  README.md                 the profile view, rendered on github.com/<user>
  assets/svg/stats.svg      four-cell stat row
  assets/svg/langs.svg      language bars
  assets/svg/streak.svg     current / longest streak + contribution total
  assets/svg/footer.svg     gradient wave sign-off

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

SITE = "https://mathewmusango.github.io/my-portfolio/"
LINKEDIN = "https://www.linkedin.com/in/mathew-musango/"
EMAIL = "musangomathew@gmail.com"

# "own"  → the committed SVG cards below (no external service, always up)
# "cards" → the familiar github-readme-stats / streak-stats images (third-party)
STATS_SOURCE = "own"

# Editorial list shared with fetch_profile.py and the hub page: one committed
# source of truth, so the icon row can change without an API round trip.
CORE_TECH = json.loads((ROOT / "data" / "core_tech.json").read_text(encoding="utf-8"))

# Things being learned (not claimed as tools) — its own committed file so the
# list can be edited without touching the script. Each entry is
# {name, note, icon}; the icon is drawn by this script (see GLYPHS).
LEARNING = json.loads((ROOT / "data" / "learning.json").read_text(encoding="utf-8"))

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

# Learning icon tiles — drawn here because no icon set carries marks for OCI,
# local-LLM work or AI-assisted workflows (checked against skillicons' tree).
GLYPH_SIZE = 48
GLYPH_TILE = "#111111"
GLYPH_INK = "#39d353"


def _glyph_cloud(ink: str) -> str:
    return (
        f'<circle cx="18.5" cy="27" r="6.5" fill="{ink}"/>'
        f'<circle cx="28" cy="24" r="9" fill="{ink}"/>'
        f'<circle cx="36" cy="29" r="5.5" fill="{ink}"/>'
        f'<rect x="14" y="29" width="22" height="6.5" rx="3.25" fill="{ink}"/>'
    )


def _glyph_chip(ink: str) -> str:
    pins = []
    for centre in (18, 24, 30):
        pins.append(f'<rect x="{centre - 1}" y="9" width="2" height="4.5" rx="1" fill="{ink}"/>')
        pins.append(f'<rect x="{centre - 1}" y="34.5" width="2" height="4.5" rx="1" fill="{ink}"/>')
        pins.append(f'<rect x="9" y="{centre - 1}" width="4.5" height="2" rx="1" fill="{ink}"/>')
        pins.append(f'<rect x="34.5" y="{centre - 1}" width="4.5" height="2" rx="1" fill="{ink}"/>')
    body = (
        f'<rect x="15" y="15" width="18" height="18" rx="3.5" fill="none" '
        f'stroke="{ink}" stroke-width="2.6"/>'
        f'<rect x="21" y="21" width="6" height="6" rx="1.5" fill="{ink}"/>'
    )
    return body + "".join(pins)


def _glyph_spark(ink: str) -> str:
    return (
        '<polygon points="24,11 27.6,20.4 37,24 27.6,27.6 24,37 20.4,27.6 11,24 20.4,20.4" '
        f'fill="{ink}"/>'
    )


GLYPHS = {"cloud": _glyph_cloud, "chip": _glyph_chip, "spark": _glyph_spark}

# Display name (as used by the hub page) → skillicons.dev slug. Names absent from
# this map simply don't appear in the icon row: skillicons has no Podman icon (and
# none for zsh, zed or archlinux either), and an unknown slug renders blank — so
# every slug added here must be probed alone first (a resolved slug returns more
# than 256 bytes; an unresolved one returns exactly 256).
SKILL_SLUGS = {
    "Kubernetes": "kubernetes",
    "Terraform": "terraform",
    "AWS": "amazonwebservices",
    "Docker": "docker",
    "Linux": "linux",
    "Arch Linux": "arch",
    "Bash": "bash",
    "GitHub Actions": "githubactions",
    "GitLab": "gitlab",
    "Python": "python",
    "HTML": "html",
    "CSS": "css",
    "JavaScript": "js",
    "MkDocs": "markdown",
    "Prometheus": "prometheus",
    "Grafana": "grafana",
}
# Always-true extras appended to the icon row.
EXTRA_SKILLS = ["git", "github"]

# Absolute raw URLs: they resolve on the profile page, in the repo view, and
def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


# Advance widths (em) for Helvetica-ish metrics — enough to centre and wrap
# text without pulling in a font library.
NARROW = {" ": 0.278, ".": 0.278, ",": 0.278, ":": 0.278, ";": 0.278, "'": 0.191,
          "!": 0.278, "|": 0.222, "(": 0.333, ")": 0.333, "-": 0.333, "/": 0.278}
WIDE = {"—": 1.0, "·": 0.35, "…": 0.9}


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
         spacing=None):
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
    return f'<text {" ".join(attributes)}>{esc(content)}</text>'


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


def cell_row(cells: list[tuple[str, str]], title: str) -> str:
    """The stat-row pattern: big value over a small uppercase label."""
    width, height = 1280, 150
    gap, margin, card_height, card_y = 20, 20, 110, 20
    card_width = (width - margin * 2 - gap * (len(cells) - 1)) / len(cells)

    body = [f'<rect width="{width}" height="{height}" fill="{BG}"/>']
    for index, (value, label) in enumerate(cells):
        x = margin + index * (card_width + gap)
        centre = x + card_width / 2
        body.append(card(x, card_y, card_width, card_height))
        body.append(text(value, centre, card_y + 58, 38, FG, anchor="middle", bold=True))
        body.append(text(label.upper(), centre, card_y + 88, 12, MUTED, anchor="middle",
                         bold=True, spacing=1.6))
    return svg(width, height, body, title)


def langs_card(languages: list[dict]) -> str:
    width, margin = 1280, 20
    inner_x = margin + 28
    inner_right = width - margin - 28
    inner_width = inner_right - inner_x

    bars, y = [], 118
    for language in languages[:6]:
        bars.append(text(language["name"], inner_x, y, 15, FG, bold=True))
        bars.append(text(f"{language['pct']:.1f}%", inner_right, y, 13, MUTED,
                         anchor="end", mono=True))
        bars.append(f'<rect x="{inner_x}" y="{y + 12}" width="{inner_width}" height="6" '
                    f'rx="3" fill="#1a1a1a"/>')
        filled = max(inner_width * language["pct"] / 100, 6)
        bars.append(f'<rect x="{inner_x}" y="{y + 12}" width="{filled:.1f}" height="6" '
                    f'rx="3" fill="url(#bar)"/>')
        y += 46

    height = int(y + 34)
    body = [
        f'<rect width="{width}" height="{height}" fill="{BG}"/>',
        card(margin, margin, width - margin * 2, height - margin * 2),
        text("Most used languages", inner_x, 68, 22, FG, bold=True),
        text("By bytes committed across public repositories", inner_right, 68, 14, MUTED,
             anchor="end"),
        *bars,
    ]
    defs = (
        '<defs><linearGradient id="bar" x1="0%" y1="0%" x2="100%" y2="0%">'
        f'<stop offset="0%" stop-color="{GREEN_BTN}"/>'
        f'<stop offset="100%" stop-color="{GREEN_BRIGHT}"/>'
        "</linearGradient></defs>"
    )
    return svg(width, height, body, "Most used languages", defs)


def wave(y: float, amplitude: float) -> str:
    return (
        f'M0,{y} C170,{y - amplitude} 320,{y + amplitude} 480,{y} '
        f'C640,{y - amplitude} 790,{y + amplitude} 960,{y} '
        f'C1120,{y - amplitude} 1180,{y + amplitude} 1280,{y} '
        "L1280,120 L0,120 Z"
    )


def footer_card() -> str:
    width, height = 1280, 120
    defs = (
        '<defs><linearGradient id="wave" x1="0%" y1="0%" x2="100%" y2="0%">'
        f'<stop offset="0%" stop-color="{GREEN_BTN}"/>'
        f'<stop offset="100%" stop-color="{GREEN_BRIGHT}"/>'
        "</linearGradient></defs>"
    )
    body = [
        f'<rect width="{width}" height="{height}" fill="{BG}"/>',
        f'<path d="{wave(74, 22)}" fill="{GREEN}" opacity="0.28"/>',
        f'<path d="{wave(92, 18)}" fill="url(#wave)" opacity="0.85"/>',
    ]
    return svg(width, height, body, "Mathew Musango Peter", defs)


def streaks(counts: list[int]) -> tuple[int, int]:
    """(current, longest) runs of consecutive days with contributions.

    A trailing zero is treated as today still in progress rather than the end of
    the streak, which is how GitHub's own streak cards behave.
    """
    longest = current = 0
    for count in counts:
        current = current + 1 if count > 0 else 0
        longest = max(longest, current)

    tail = counts[:-1] if counts and counts[-1] == 0 else counts
    trailing = 0
    for count in reversed(tail):
        if count <= 0:
            break
        trailing += 1
    return trailing, longest


def skill_row(core_tech: list[str]) -> str:
    slugs = [SKILL_SLUGS[name] for name in core_tech if name in SKILL_SLUGS] + EXTRA_SKILLS
    display = {slug: name for name, slug in SKILL_SLUGS.items()}
    display.update({"git": "Git", "github": "GitHub"})
    alt = ", ".join(display.get(slug, slug) for slug in slugs)
    return (
        f'<p align="center">\n'
        f'  <a href="{SITE}">\n'
        f'    <img src="https://skillicons.dev/icons?i={",".join(slugs)}&perline=10" '
        f'alt="{esc(alt)}" />\n  </a>\n</p>'
    )


def badges() -> str:
    def badge(label, message, colour, logo, href, alt):
        url = (f"https://img.shields.io/badge/{label}-{message}-{colour}"
               f"?style=for-the-badge&logo={logo}&logoColor=white")
        return f'<a href="{href}" title="{alt}"><img src="{url}" alt="{alt}" height="30" align="center" /></a>'

    return " ".join(
        [
            badge("Website", "mathewmusango.github.io", "26a641", "googlechrome", SITE,
                  "Portfolio"),
            badge("LinkedIn", "Connect", "0077B5", "linkedin", LINKEDIN, "LinkedIn"),
            badge("Email", EMAIL, "D14836", "gmail", f"mailto:{EMAIL}", "Email"),
            badge("GitHub", USER, "181717", "github", f"https://github.com/{USER}",
                  "GitHub profile"),
        ]
    )


def own_stats(snapshot: dict) -> str:
    images = [
        f'{RAW}/assets/svg/stats.svg',
        f'{RAW}/assets/svg/langs.svg',
        f'{RAW}/assets/svg/streak.svg',
    ]
    alts = [
        f"{snapshot['stats']['repos']} public repositories, {snapshot['stats']['stars']} stars, "
        f"{snapshot['stats']['followers']} followers, {snapshot['stats']['years_active']} years active",
        "Most used languages by bytes committed",
        "Current streak, longest streak and contributions in the last year",
    ]
    return "\n".join(
        f'<p align="center">\n  <img src="{src}" alt="{esc(alt)}" width="100%">\n</p>'
        for src, alt in zip(images, alts)
    )


def third_party_stats() -> str:
    theme = "theme=github_dark&hide_border=true"
    return "\n".join(
        [
            f'<p align="center">\n  <a href="https://github.com/{USER}">\n'
            f'    <img src="https://github-readme-stats.vercel.app/api?username={USER}'
            f'&show_icons=true&{theme}" alt="GitHub stats" />\n  </a>\n</p>',
            f'<p align="center">\n  <a href="https://github.com/{USER}">\n'
            f'    <img src="https://github-readme-stats.vercel.app/api/top-langs/?username={USER}'
            f'&layout=compact&{theme}" alt="Top languages" />\n  </a>\n</p>',
            f'<p align="center">\n  <a href="https://github.com/{USER}">\n'
            f'    <img src="https://streak-stats.demolab.com/?user={USER}&theme=github-dark'
            f'&hide_border=true" alt="Contribution streak" />\n  </a>\n</p>',
        ]
    )


def learning_section() -> str:
    """The Learning sub-section: a centred row of our own icon tiles.

    No icon set carries marks for OCI, local-LLM work or AI-assisted workflows
    (checked against skillicons' tree), so the tiles are drawn here. Each <img>
    carries a title attribute — GitHub preserves it, so hovering shows the
    name and note.
    """
    if not LEARNING:
        return ""
    images = []
    for item in LEARNING:
        if not item.get("icon"):
            continue
        tooltip = item["name"]
        if item.get("note"):
            tooltip += " — " + item["note"]
        images.append(
            f'<img src="{RAW}/assets/svg/icons/{item["icon"]}.svg" '
            f'alt="{esc(item["name"])}" title="{esc(tooltip)}" '
            f'width="{GLYPH_SIZE}" height="{GLYPH_SIZE}">'
        )
    if not images:
        return ""
    joined = "\n  ".join(images)
    return f"\n### 📚 Learning\n\n<p align=\"center\">\n  {joined}\n</p>\n"


def write_learning_icons(icons: list[str]) -> list[pathlib.Path]:
    out_dir = ROOT / "assets" / "svg" / "icons"
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name in sorted(set(icons)):
        glyph = GLYPHS.get(name)
        if not glyph:
            continue
        body = [
            f'<rect x="0.5" y="0.5" width="{GLYPH_SIZE - 1}" height="{GLYPH_SIZE - 1}" '
            f'rx="10" fill="{GLYPH_TILE}" stroke="{BORDER}"/>',
            glyph(GLYPH_INK),
        ]
        path = out_dir / f"{name}.svg"
        path.write_text(svg(GLYPH_SIZE, GLYPH_SIZE, body, f"{name} — learning"),
                        encoding="utf-8")
        written.append(path)
    return written


def readme(snapshot: dict) -> str:
    refreshed = dt.date.fromisoformat(snapshot["generated"][:10]).strftime("%d %B %Y")
    stats = own_stats(snapshot) if STATS_SOURCE == "own" else third_party_stats()

    # The Learning sub-section only exists while the list is non-empty.
    learning = learning_section()

    return f"""<!-- Generated by scripts/build_readme.py — edit the script, not this file. -->

<p align="center">
  {badges()}
</p>

## 🛠️ Languages and Tools

{skill_row(CORE_TECH)}
{learning}
## 📊 GitHub Stats

{stats}

<p align="center">
  <img src="{RAW}/assets/svg/footer.svg" alt="" width="100%">
</p>

<sub>Statistics, cards and this README are generated from GitHub's public API by
<a href="https://github.com/{USER}/{USER}/blob/{BRANCH}/scripts/build_readme.py"><code>scripts/build_readme.py</code></a>
— last refreshed {refreshed}. Contribution activity below is rendered natively by GitHub.</sub>
"""


def main() -> None:
    snapshot = json.loads((ROOT / "data" / "profile.json").read_text(encoding="utf-8"))

    svg_dir = ROOT / "assets" / "svg"
    svg_dir.mkdir(parents=True, exist_ok=True)

    # Cards this script no longer renders (it replaced the banner and the
    # combined tech card with a skill-icon row and a languages card).
    for stale in ("hero.svg", "tech.svg"):
        (svg_dir / stale).unlink(missing_ok=True)

    current, longest = streaks(snapshot["contributions"]["counts"])
    (svg_dir / "stats.svg").write_text(
        cell_row(
            [
                (compact(snapshot["stats"]["repos"]), "Total repos"),
                (compact(snapshot["stats"]["stars"]), "All stars"),
                (compact(snapshot["stats"]["followers"]), "Followers"),
                (str(snapshot["stats"]["years_active"]), "Years active"),
            ],
            "Repositories, stars, followers and years active",
        ),
        encoding="utf-8",
    )
    (svg_dir / "langs.svg").write_text(langs_card(snapshot["languages"]), encoding="utf-8")
    (svg_dir / "streak.svg").write_text(
        cell_row(
            [
                (f"{current}d", "Current streak"),
                (f"{longest}d", "Longest streak"),
                (compact(snapshot["contributions"]["total"]), "Contributions"),
            ],
            "Contribution streaks",
        ),
        encoding="utf-8",
    )
    (svg_dir / "footer.svg").write_text(footer_card(), encoding="utf-8")
    (ROOT / "README.md").write_text(readme(snapshot), encoding="utf-8")
    learning_icons = write_learning_icons(
        [item["icon"] for item in LEARNING if item.get("icon")]
    )

    print(f"wrote README.md (stats source: {STATS_SOURCE})")
    print(f"streaks: current {current}d, longest {longest}d")
    for name in ("stats", "langs", "streak", "footer"):
        path = svg_dir / f"{name}.svg"
        print(f"wrote assets/svg/{name}.svg  {path.stat().st_size / 1024:.1f} KiB")
    for path in learning_icons:
        print(f"wrote assets/svg/icons/{path.name}")


if __name__ == "__main__":
    main()
