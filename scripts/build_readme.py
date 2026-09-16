#!/usr/bin/env python3
"""Render the profile README.

GitHub renders this repository's ``README.md`` on ``github.com/<user>``, and a
profile page accepts nothing but markdown and a sanitised subset of HTML — no
CSS, no scripts, no classes. So the page is assembled from:

* shields.io **static** badges (no integration that can go stale),
* one skillicons.dev image for the tool row,
* SVG tiles drawn here for the Learning rows, plus the wave sign-off.

The only inputs are the two editorial lists in ``data/`` — there is no API call,
no token and nothing to schedule.

Writes:
  README.md
  assets/svg/icons/*.svg   one tile per Learning entry
  assets/svg/footer.svg    the wave sign-off

Run:
  python3 scripts/build_readme.py
"""

from __future__ import annotations

import html
import json
import pathlib

USER = "mathewmusango"
BRANCH = "main"
ROOT = pathlib.Path(__file__).resolve().parent.parent

# Image references are repo-relative by default: they resolve in a local preview,
# in the GitHub repo view, and on the profile page (GitHub renders the profile
# README with the repository as context). Set IMAGE_BASE to RAW to force absolute
# raw.githubusercontent.com URLs instead.
RAW = f"https://raw.githubusercontent.com/{USER}/{USER}/{BRANCH}"
IMAGE_BASE = ""

SITE = "https://mathewmusango.github.io/my-portfolio/"
LINKEDIN = "https://www.linkedin.com/in/mathew-musango/"
EMAIL = "musangomathew@gmail.com"

CORE_TECH = json.loads((ROOT / "data" / "core_tech.json").read_text(encoding="utf-8"))
LEARNING = json.loads((ROOT / "data" / "learning.json").read_text(encoding="utf-8"))

# Display name (as used in data/core_tech.json) → skillicons.dev slug. Names absent
# from this map simply don't appear in the icon row: skillicons has no Podman icon
# (and none for zsh, zed or archlinux either), and an unknown slug renders blank —
# so every slug added here must be probed alone first (a resolved slug returns more
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
    "Obsidian": "obsidian",
    "Elasticsearch": "elasticsearch",
}
# Always-true extras appended to the icon row.
EXTRA_SKILLS = ["git", "github"]

BG = "#030303"
BORDER = "#222222"
GREEN = "#26a641"
GREEN_BRIGHT = "#39d353"
GREEN_BTN = "#238636"

# Learning icon tiles — drawn here because no icon set carries marks for OCI,
# local-LLM work, AI-assisted workflows, PKI, tracing or GitOps.
GLYPH_SIZE = 48
GLYPH_TILE = "#111111"
GLYPH_INK = "#39d353"


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


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


def _glyph_server(ink: str) -> str:
    units = []
    for y in (13, 26):
        units.append(
            f'<rect x="12" y="{y}" width="24" height="9.5" rx="2.5" fill="none" '
            f'stroke="{ink}" stroke-width="2.4"/>'
            f'<circle cx="16.6" cy="{y + 4.75}" r="1.6" fill="{ink}"/>'
            f'<rect x="21" y="{y + 3.6}" width="11" height="2.2" rx="1.1" fill="{ink}"/>'
        )
    return "".join(units)


def _glyph_key(ink: str) -> str:
    return (
        f'<circle cx="17" cy="24" r="6.2" fill="none" stroke="{ink}" stroke-width="2.6"/>'
        f'<rect x="22" y="22.6" width="14" height="2.8" rx="1.4" fill="{ink}"/>'
        f'<rect x="29.5" y="25.4" width="2.6" height="4.6" rx="1.3" fill="{ink}"/>'
        f'<rect x="33.5" y="25.4" width="2.6" height="6.4" rx="1.3" fill="{ink}"/>'
    )


def _glyph_chart(ink: str) -> str:
    return (
        f'<polyline points="12,33 19.5,25.5 25,29.5 36,15.5" fill="none" stroke="{ink}" '
        f'stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<rect x="11" y="35.2" width="26" height="2.4" rx="1.2" fill="{ink}"/>'
    )


def _glyph_cube(ink: str) -> str:
    return (
        f'<polygon points="24,10.5 35.5,17 35.5,31 24,37.5 12.5,31 12.5,17" fill="none" '
        f'stroke="{ink}" stroke-width="2.6" stroke-linejoin="round"/>'
        f'<polygon points="24,10.5 35.5,17 24,23.5 12.5,17" fill="{ink}" opacity="0.5"/>'
        f'<rect x="22.8" y="23.2" width="2.4" height="14" fill="{ink}" opacity="0.5"/>'
    )


def _glyph_pipeline(ink: str) -> str:
    chevrons = []
    for x in (11, 20.5, 30):
        chevrons.append(
            f'<polygon points="{x},14 {x + 7.5},24 {x},34 {x + 3.2},24" fill="{ink}"/>'
        )
    return "".join(chevrons)


GLYPHS = {
    "cloud": _glyph_cloud,
    "chip": _glyph_chip,
    "spark": _glyph_spark,
    "server": _glyph_server,
    "key": _glyph_key,
    "chart": _glyph_chart,
    "cube": _glyph_cube,
    "pipeline": _glyph_pipeline,
}


def _wave(y: float, amplitude: float) -> str:
    return (
        f"M0,{y} C170,{y - amplitude} 320,{y + amplitude} 480,{y} "
        f"C640,{y - amplitude} 790,{y + amplitude} 960,{y} "
        f"C1120,{y - amplitude} 1180,{y + amplitude} 1280,{y} "
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
        f'<path d="{_wave(74, 22)}" fill="{GREEN}" opacity="0.28"/>',
        f'<path d="{_wave(92, 18)}" fill="url(#wave)" opacity="0.85"/>',
    ]
    return svg(width, height, body, "Mathew Musango Peter", defs)


def badges() -> str:
    def badge(label, message, colour, logo, href, alt):
        url = (
            f"https://img.shields.io/badge/{label}-{message}-{colour}"
            f"?style=for-the-badge&logo={logo}&logoColor=white"
        )
        return (
            f'<a href="{href}" title="{alt}"><img src="{url}" alt="{alt}" height="30" '
            f'align="center" /></a>'
        )

    return " ".join(
        [
            badge("Website", "mathewmusango.github.io", "26a641", "googlechrome", SITE, "Portfolio"),
            badge("LinkedIn", "Connect", "0077B5", "linkedin", LINKEDIN, "LinkedIn"),
            badge("Email", EMAIL, "D14836", "gmail", f"mailto:{EMAIL}", "Email"),
            badge("GitHub", USER, "181717", "github", f"https://github.com/{USER}", "GitHub profile"),
        ]
    )


def skill_row() -> str:
    slugs = [SKILL_SLUGS[name] for name in CORE_TECH if name in SKILL_SLUGS] + EXTRA_SKILLS
    display = {slug: name for name, slug in SKILL_SLUGS.items()}
    display.update({"git": "Git", "github": "GitHub"})
    alt = ", ".join(display.get(slug, slug) for slug in slugs)
    return (
        '<p align="center">\n'
        f'  <a href="{SITE}">\n'
        f'    <img src="https://skillicons.dev/icons?i={",".join(slugs)}&perline=10" '
        f'alt="{esc(alt)}" />\n  </a>\n</p>'
    )


def learning_section() -> str:
    """The Learning sub-section: a centred row of our own icon tiles.

    Each <img> carries a title attribute — GitHub preserves it in rendered
    READMEs, so hovering shows the name and note — and alt for assistive tech.
    """
    images = []
    for item in LEARNING:
        if not item.get("icon"):
            continue
        tooltip = item["name"] + (" — " + item["note"] if item.get("note") else "")
        images.append(
            f'<img src="{IMAGE_BASE}assets/svg/icons/{item["icon"]}.svg" '
            f'alt="{esc(item["name"])}" title="{esc(tooltip)}" '
            f'width="{GLYPH_SIZE}" height="{GLYPH_SIZE}">'
        )
    if not images:
        return ""
    joined = "\n  ".join(images)
    return f'\n### 📚 Learning\n\n<p align="center">\n  {joined}\n</p>\n'


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
        path.write_text(svg(GLYPH_SIZE, GLYPH_SIZE, body, f"{name} — learning"), encoding="utf-8")
        written.append(path)

    # Tiles whose entry was removed don't belong in the repo.
    keep = {path.name for path in written}
    for stale in out_dir.glob("*.svg"):
        if stale.name not in keep:
            stale.unlink()

    return written


def readme() -> str:
    return f"""<!-- Generated by scripts/build_readme.py — edit the script, not this file. -->

<p align="center">
  {badges()}
</p>

## 🛠️ Languages and Tools

{skill_row()}
{learning_section()}
<p align="center">
  <img src="{IMAGE_BASE}assets/svg/footer.svg" alt="" width="100%">
</p>

<sub>Badges, icons and this README are generated by
<code>scripts/build_readme.py</code> from the lists in <code>data/</code>.
Contribution activity below is rendered natively by GitHub.</sub>
"""


def main() -> None:
    icons = write_learning_icons([item["icon"] for item in LEARNING if item.get("icon")])

    svg_dir = ROOT / "assets" / "svg"
    svg_dir.mkdir(parents=True, exist_ok=True)
    (svg_dir / "footer.svg").write_text(footer_card(), encoding="utf-8")
    (ROOT / "README.md").write_text(readme(), encoding="utf-8")

    print("wrote README.md")
    print("wrote assets/svg/footer.svg")
    for path in icons:
        print(f"wrote assets/svg/icons/{path.name}")


if __name__ == "__main__":
    main()
