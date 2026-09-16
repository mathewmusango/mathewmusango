#!/usr/bin/env python3
"""Render the profile README.

GitHub renders this repository's ``README.md`` on ``github.com/<user>``, and a
profile page accepts nothing but markdown and a sanitised subset of HTML — no
CSS, no scripts, no classes. So the page is assembled from:

* shields.io **static** badges (the contact row),
* flat monochrome brand glyphs from the Simple Icons CDN for the tool row,
  plus one locally committed glyph for AWS, which Simple Icons no longer carries,
* SVG tiles drawn here for the Learning row and the wave sign-off.

Every icon is a separate ``<img>`` carrying ``title`` (a hover tooltip) and
``alt``, and every row is centred, because these two sections *are* the page.
The only inputs are the two editorial lists in ``data/``.

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
import urllib.parse

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

# Display name (as used in data/core_tech.json) → Simple Icons slug. Names absent
# from this map don't appear in the row at all, so adding an entry there means
# adding a mapping here too. Each slug must be probed before it is trusted:
# https://cdn.simpleicons.org/<slug>/<colour> answers 404 with a zero-byte body
# when the icon does not exist — which is how `amazonaws` was found to have been
# withdrawn from the set (see LOCAL_BRANDS below).
BRAND_SLUGS = {
    "Kubernetes": "kubernetes",
    "Terraform": "terraform",
    "Docker": "docker",
    "Podman": "podman",
    "Linux": "linux",
    "Arch Linux": "archlinux",
    "Bash": "gnubash",
    "Zsh": "zsh",
    "GitHub Actions": "githubactions",
    "GitLab": "gitlab",
    "Python": "python",
    "HTML": "html5",
    "CSS": "css",
    "JavaScript": "javascript",
    "MkDocs": "markdown",
    "Prometheus": "prometheus",
    "Grafana": "grafana",
    "Obsidian": "obsidian",
    "Elasticsearch": "elasticsearch",
    "Git": "git",
    "GitHub": "github",
    "AWS": "amazonaws",
}
# Brands kept in the repo because the CDN no longer serves them. AWS was removed
# from Simple Icons at Amazon's request, so the mark is committed here instead —
# see assets/svg/brands/README.md.
LOCAL_BRANDS = {"amazonaws"}

ICON_SIZE = 30
CDN = "https://cdn.simpleicons.org"

# Icons are served in each vendor's own colour. A brand colour that fails WCAG's 3:1
# contrast on GitHub's white or dark canvas gets a tint for that theme only, computed
# from the brand hex by mixing towards black (light theme) or white (dark theme) so the
# hue survives and the glyph stays legible either way. Only the brands that need it are
# listed; everything else is served in its official colour. DARK_MARK_BG is GitHub's
# dark canvas, used when these values were derived.
THEME_COLOURS = {
    "css": {"dark": "baa3d1"},
    "elasticsearch": {"dark": "8cb2bf"},
    "github": {"dark": "979797"},
    "gitlab": {"light": "8b3c15"},
    "gnubash": {"light": "2b5e14"},
    "javascript": {"light": "887b10"},
    "linux": {"light": "8b6d14"},
    "markdown": {"dark": "8c8c8c"},
    "openssl": {"dark": "c09594"},
    "opentelemetry": {"dark": "8c8c8c"},
    "podman": {"dark": "caa0d4"},
    "qemu": {"light": "8c3800"},
}

BG = "#030303"
BORDER = "#222222"
GREEN = "#26a641"
GREEN_BRIGHT = "#39d353"
GREEN_BTN = "#238636"

# Learning tiles — drawn here because no icon set carries marks for OCI,
# local-LLM work, AI-assisted workflows, PKI, tracing or GitOps.
GLYPH_BOX = 48
GLYPH_VIEW = "6 6 36 36"  # trims the drawing's margin so it optically matches CDN glyphs
GLYPH_INK = GREEN_BRIGHT


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


def svg(width: int, height: int, body: list[str], title: str, defs: str = "",
        view_box: str | None = None) -> str:
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="{view_box or f"0 0 {width} {height}"}" role="img" '
            f'aria-label="{esc(title)}">',
            f"<title>{esc(title)}</title>",
            defs,
            *body,
            "</svg>",
            "",
        ]
    )


def _glyph_cloud(ink: str) -> str:
    return (
        f'<circle cx="15.5" cy="27" r="6.5" fill="{ink}"/>'
        f'<circle cx="25" cy="24" r="9" fill="{ink}"/>'
        f'<circle cx="33" cy="29" r="5.5" fill="{ink}"/>'
        f'<rect x="11" y="29" width="22" height="6.5" rx="3.25" fill="{ink}"/>'
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
        f'stroke="{ink}" stroke-width="3.2"/>'
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
            f'stroke="{ink}" stroke-width="3"/>'
            f'<circle cx="16.6" cy="{y + 4.75}" r="1.8" fill="{ink}"/>'
            f'<rect x="21" y="{y + 3.6}" width="11" height="2.4" rx="1.2" fill="{ink}"/>'
        )
    return "".join(units)


def _glyph_key(ink: str) -> str:
    return (
        f'<circle cx="17" cy="24" r="6.2" fill="none" stroke="{ink}" stroke-width="3.2"/>'
        f'<rect x="22" y="22.4" width="14" height="3.2" rx="1.6" fill="{ink}"/>'
        f'<rect x="29.5" y="25.4" width="3" height="4.6" rx="1.5" fill="{ink}"/>'
        f'<rect x="33.5" y="25.4" width="3" height="6.4" rx="1.5" fill="{ink}"/>'
    )


def _glyph_chart(ink: str) -> str:
    return (
        f'<polyline points="12,33 19.5,25.5 25,29.5 36,15.5" fill="none" stroke="{ink}" '
        f'stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>'
        f'<rect x="11" y="35.2" width="26" height="2.8" rx="1.4" fill="{ink}"/>'
    )


def _glyph_cube(ink: str) -> str:
    return (
        f'<polygon points="24,10.5 35.5,17 35.5,31 24,37.5 12.5,31 12.5,17" fill="none" '
        f'stroke="{ink}" stroke-width="3.2" stroke-linejoin="round"/>'
        f'<polygon points="24,10.5 35.5,17 24,23.5 12.5,17" fill="{ink}" opacity="0.5"/>'
        f'<rect x="22.6" y="23.2" width="2.8" height="14" fill="{ink}" opacity="0.5"/>'
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

    return "\n  ".join(
        [
            badge("Website", "mathewmusango.github.io", "26a641", "googlechrome", SITE, "Portfolio"),
            badge("LinkedIn", "Connect", "0077B5", "linkedin", LINKEDIN, "LinkedIn"),
            badge("Email", EMAIL, "D14836", "gmail", f"mailto:{EMAIL}", "Email"),
            badge("GitHub", USER, "181717", "github", f"https://github.com/{USER}", "GitHub profile"),
        ]
    )


def icon(src: str, name: str, tooltip: str | None = None,
         src_dark: str | None = None) -> str:
    """An ``<img>``, or a ``<picture>`` when the mark needs a per-theme colour."""
    label = tooltip or name
    attributes = (
        f'alt="{esc(name)}" title="{esc(label)}" width="{ICON_SIZE}" height="{ICON_SIZE}"'
    )
    if not src_dark:
        return f'<img src="{src}" {attributes}>'
    return (
        "<picture>\n"
        f'    <source media="(prefers-color-scheme: dark)" srcset="{src_dark}">\n'
        f'    <img src="{src}" {attributes}>\n'
        "  </picture>"
    )


def vendor_icon(slug: str, name: str, tooltip: str | None = None) -> str:
    """A CDN glyph in the vendor's colour, with a theme tint only if it needs one."""
    base = f"{CDN}/{urllib.parse.quote(slug)}"
    fix = THEME_COLOURS.get(slug, {})
    light = f'{base}/{fix["light"]}' if fix.get("light") else base
    dark = f'{base}/{fix["dark"]}' if fix.get("dark") else None
    return icon(light, name, tooltip, dark)


def tool_row() -> str:
    """One vendor-coloured glyph per tool, named in the tooltip."""
    icons = []
    for name in CORE_TECH:
        slug = BRAND_SLUGS.get(name)
        if not slug:
            continue
        if slug in LOCAL_BRANDS:
            icons.append(icon(f"{IMAGE_BASE}assets/svg/brands/{slug}.svg", name))
        else:
            icons.append(vendor_icon(slug, name))
    return "\n  &nbsp;\n  ".join(icons)


def learning_row() -> str:
    """Vendor marks where the subject is a real product, our own marks where it is an
    area: OCI (no mark exists), local-LLM work (no runtime chosen), AI-assisted
    workflows, Terraform modules and GitOps."""
    icons = []
    for item in LEARNING:
        name = item["name"]
        tooltip = name + (" — " + item["note"] if item.get("note") else "")
        if item.get("slug"):
            icons.append(vendor_icon(item["slug"], name, tooltip))
        elif item.get("glyph"):
            icons.append(
                icon(f'{IMAGE_BASE}assets/svg/icons/{item["glyph"]}.svg', name, tooltip)
            )
    return "\n  &nbsp;\n  ".join(icons)


def write_learning_icons(icons: list[str]) -> list[pathlib.Path]:
    out_dir = ROOT / "assets" / "svg" / "icons"
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for name in sorted(set(icons)):
        glyph = GLYPHS.get(name)
        if not glyph:
            continue
        path = out_dir / f"{name}.svg"
        path.write_text(
            svg(GLYPH_BOX, GLYPH_BOX, [glyph(GLYPH_INK)], f"{name} — learning",
                view_box=GLYPH_VIEW),
            encoding="utf-8",
        )
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

<h3 align="center">Languages and Tools</h3>

<p align="center">
  {tool_row()}
</p>

<h3 align="center">Learning</h3>

<p align="center">
  {learning_row()}
</p>

<p align="center">
  <img src="{IMAGE_BASE}assets/svg/footer.svg" alt="" width="100%">
</p>
"""


def main() -> None:
    icons = write_learning_icons([item["glyph"] for item in LEARNING if item.get("glyph")])

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
