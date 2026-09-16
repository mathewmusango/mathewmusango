# mathewmusango — development notes

This repository exists to put a README on <https://github.com/mathewmusango>. Nothing else belongs
in it: a profile repo's job is the README, and every file below is either that README, an input it
is generated from, or the two scripts that draw it.

## What GitHub requires for the profile view

All four must hold ([docs](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme)):

- the repository is named exactly like the account — `mathewmusango`;
- **the repository is public** — making it private removes the profile view;
- `README.md` exists at the root and is not empty.

Two footnotes from the same page: profile READMEs are unavailable to *managed user accounts*, and a
repo that existed before July 2020 needs "Share to profile" — neither applies here.

## What lives here

| Path | Why |
| --- | --- |
| `README.md` | **Generated** — the profile view. Edit the scripts, never this file |
| `assets/svg/{stats,langs,streak,footer}.svg` | **Generated** cards |
| `assets/svg/icons/*.svg` | **Generated** Learning tiles (`cloud`, `chip`, `spark`, `server`, `key`) |
| `data/profile.json` | **Generated** snapshot of GitHub's public API |
| `data/core_tech.json` | Editorial tool list → the skill-icon row |
| `data/learning.json` | Editorial `{name, note, icon}` rows → the Learning tiles |
| `scripts/fetch_profile.py` | Refreshes the snapshot (public endpoints, no token) |
| `scripts/build_readme.py` | Draws the cards and writes `README.md` |
| `.github/workflows/refresh-readme.yml` | Daily: refresh, redraw, commit |

An earlier version of this repo also carried a standalone "hub page" (`index.html` + its CSS/JS) and
a GitHub Pages deploy. Both were removed on request — GitHub needs only the README — and are
recoverable from git history up to commit `150d2aa`.

## Refresh

```sh
python3 scripts/fetch_profile.py   # data/profile.json (needs network)
python3 scripts/build_readme.py    # README.md + assets/svg/** (offline)
```

`fetch_profile.py` uses only public, **unauthenticated** endpoints: the user record (followers, join
date), the repository list, per-repo language bytes, and GitHub's contribution calendar. It needs no
token. The daily workflow runs both scripts and commits whatever moved — the README's "last
refreshed" date changes daily, so a daily commit is expected.

## How the README is assembled

| Piece | Rendered by | Notes |
| --- | --- | --- |
| Contact badges | shields.io | **Static** badges only — no third-party integration that can go stale |
| Languages and tools | skillicons.dev | Slugs mapped from `data/core_tech.json`. Each slug must be probed alone: a resolved slug returns more than 256 bytes, an unresolved one exactly 256. **Podman has no icon** (nor do zsh, zed or archlinux), so it is skipped rather than rendered blank |
| Learning sub-section | **our own tiles** | `write_learning_icons()` draws them — no icon set carries OCI, LLM, AI-workflow or PKI marks. Each `<img>` carries `title` (name — note) for a hover tooltip and `alt` for assistive tech; the whole section disappears when the list is empty |
| GitHub stats | **our own cards** | `stats`, `langs`, `streak`, embedded with `<img width="100%">`. `STATS_SOURCE = "cards"` swaps in github-readme-stats + streak-stats instead |
| Wave sign-off | **our own card** | `footer.svg` |
| Contribution graph | GitHub | Rendered natively below the README — nothing to do |

**Image paths are repo-relative** (`assets/svg/…`). They resolve in a local preview, in the repo
view, and on the profile page — GitHub renders the profile README with the repository as context.
Absolute `raw.githubusercontent.com` URLs were used at first and 404'd until the repo existed, so
*every* image was broken pre-push; `IMAGE_BASE` in `build_readme.py` switches to absolute in one
constant if that is ever needed.

Card text is positioned with an approximate Helvetica metric table, so headings and labels centre
and wrap without a font library. Streaks are derived from the calendar in the snapshot (a trailing
zero-day counts as "today in progress").

## Editing

- **Tool list** → `data/core_tech.json`. Names missing from `SKILL_SLUGS` in `build_readme.py` simply
  don't appear in the icon row; add a mapping after probing that the slug resolves.
- **Learning list** → `data/learning.json`; `icon` must be a key in `GLYPHS`, or add a glyph function.
- **Badge targets** → `SITE`, `LINKEDIN`, `EMAIL` in `build_readme.py` (`USER`, `BRANCH` too).
- **Palette** → the colour constants at the top of `build_readme.py`.
