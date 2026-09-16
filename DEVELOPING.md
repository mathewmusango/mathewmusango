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
python3 scripts/fetch_profile.py                        # public data only
GITHUB_TOKEN=<token> python3 scripts/fetch_profile.py   # + private repositories
python3 scripts/build_readme.py                         # README.md + assets/svg/** (offline)
```

`fetch_profile.py` reads the user record (followers, join date), the repository list, per-repo
language bytes and GitHub's contribution calendar.

**Public vs private repositories.** `REPO_SCOPE` at the top of the script is `"all"` by default:
with a token, the repository count, star total and language mix cover **public and private** repos
and `stats.scope` becomes `"all"`; set `REPO_SCOPE = "public"` to keep the numbers public-only even
when a token is present. Without a token — or with one the API rejects, which prints a warning and
carries on — the snapshot falls back to public data. The workflow passes `secrets.PROFILE_TOKEN`,
so save a read-only token under that name; leaving the secret unset breaks nothing.

**Private contributions are not a script setting** — they are a GitHub profile option. Turn on
"Include private contributions on my profile" and both the calendar read here and GitHub's own graph
will include them.

**Is this realtime?** No — it is a **snapshot**, refreshed on a schedule. GitHub renders committed
markdown, so the cards only move when the workflow commits new ones (up to ~24 h stale; tighten the
cron for fresher, at the cost of a commit each run). A genuinely live number would need a
third-party card service that renders on each view — that is what `STATS_SOURCE = "cards"` switches
to. The contribution graph below the README is GitHub's own, so it is always current.

## How the README is assembled

| Piece | Rendered by | Notes |
| --- | --- | --- |
| Contact badges | shields.io | **Static** badges only — no third-party integration that can go stale |
| Languages and tools | skillicons.dev | Slugs mapped from `data/core_tech.json`. Each slug must be probed alone: a resolved slug returns more than 256 bytes, an unresolved one exactly 256. **Podman has no icon** (nor do zsh, zed or archlinux), so it is skipped rather than rendered blank |
| Learning sub-section | **our own tiles** | `write_learning_icons()` draws them from `GLYPHS` (`cloud`, `chip`, `spark`, `server`, `key`, `chart`, `cube`, `pipeline`) — no icon set carries OCI, LLM, AI-workflow, PKI, tracing or GitOps marks. Each `<img>` carries `title` (name — note) for a hover tooltip and `alt` for assistive tech; the whole section disappears when the list is empty |
| GitHub stats | **our own cards** | `stats`, `langs`, `streak`, embedded with `<img width="100%">`. Public-only or public+private, per the token above. `STATS_SOURCE = "cards"` swaps in github-readme-stats + streak-stats instead |
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
