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

# Display name (as used by the hub page) → skillicons.dev slug.
SKILL_SLUGS = {
    "Kubernetes": "kubernetes",
    "Terraform": "terraform",
    "AWS": "amazonwebservices",
    "Docker": "docker",
    "Podman": "podman",
    "Linux": "linux",
    "GitHub Actions": "githubactions",
    "Python": "python",
    "Bash": "bash",
    "MkDocs": "markdown",
    "Prometheus": "prometheus",
    "Grafana": "grafana",
}
# Always-true extras appended to the icon row.
EXTRA_SKILLS = ["git", "github"]

# Editorial copy — review these lines, they are the voice of the page.
BULLETS = [
    ("🔭", f"Currently building a tri-lingual cloud-resume platform on AWS — "
            f"[S3 + CloudFront, Terraform, OIDC deploys]({SITE})"),
    ("🌱", "Working in the open on **platform engineering**: reusable CI, "
            "infrastructure as code, privacy-first observability"),
    ("👯", "Open to collaboration on **cloud-native**, **platform engineering** and "
            "**DevSecOps** projects — fork anything here"),
    ("💬", "Ask me about **Kubernetes · Terraform · AWS · CI/CD · observability · "
            "PCI-DSS compliance**"),
    ("⚡", "I automate anything I have to do twice"),
]


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


def readme(snapshot: dict) -> str:
    refreshed = dt.date.fromisoformat(snapshot["generated"][:10]).strftime("%d %B %Y")
    bullets = "\n".join(f"- {emoji} {line}" for emoji, line in BULLETS)
    stats = own_stats(snapshot) if STATS_SOURCE == "own" else third_party_stats()

    return f"""<!-- Generated by scripts/build_readme.py — edit the script, not this file. -->

{bullets}
- 📫 Reach me: {badges()}

## 🛠️ Languages and Tools

{skill_row(snapshot['core_tech'])}

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

    print(f"wrote README.md (stats source: {STATS_SOURCE})")
    print(f"streaks: current {current}d, longest {longest}d")
    for name in ("stats", "langs", "streak", "footer"):
        path = svg_dir / f"{name}.svg"
        print(f"wrote assets/svg/{name}.svg  {path.stat().st_size / 1024:.1f} KiB")


if __name__ == "__main__":
    main()
