# mathewmusango — development notes

This repository exists to put a README on <https://github.com/mathewmusango>. Nothing else belongs
in it, and nothing in it talks to the network: the page is assembled from two committed lists, so
there is no API call, no token, no snapshot and nothing to schedule.

## What GitHub requires for the profile view

All of these must hold ([docs](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme)):

- the repository is named exactly like the account — `mathewmusango`;
- **the repository is public** — making it private removes the profile view;
- `README.md` exists at the root and is not empty.

Footnotes from the same page: profile READMEs are unavailable to *managed user accounts*, and a repo
that existed before July 2020 needs "Share to profile" — neither applies here.

## What lives here

| Path | Why |
| --- | --- |
| `README.md` | **Generated** — the profile view. Edit the script or the lists, never this file |
| `assets/svg/icons/*.svg` | **Generated** Learning tiles (`cloud`, `chip`, `spark`, `server`, `key`, `chart`, `cube`, `pipeline`) |
| `assets/svg/footer.svg` | **Generated** wave sign-off |
| `data/core_tech.json` | The tool list → the skill-icon row |
| `data/learning.json` | `{name, note, icon}` rows → the Learning tiles |
| `scripts/build_readme.py` | Draws all of it and writes `README.md` |
| `DEVELOPING.md` | This file |

**Removed, and recoverable from git history:** a standalone hub page (`index.html` + CSS/JS, up to
`150d2aa`); and the GitHub *stat* cards — repo/star/follower counts, language bars and a streak card
— together with the fetcher, the API snapshot and the daily refresh workflow that fed them (up to
`879fe3f`). The stats were dropped at the user's request; the fetcher went with them because nothing
consumed its data any more. Restore both with `git revert` or by re-adding those paths.

## Build

```sh
python3 scripts/build_readme.py   # README.md + assets/svg/** — offline, no dependencies
```

It prunes Learning tiles whose entry has been removed, so deleting an item from the list cleans up
after itself.

Preview: open `README.md` in Zed and *Open Preview* (`ctrl-k v`) — relative image paths resolve
locally, so no push is needed to see the result.

## How the README is assembled

| Piece | Rendered by | Notes |
| --- | --- | --- |
| Contact badges | shields.io | **Static** badges only — no third-party integration that can go stale |
| Languages and tools | skillicons.dev | Slugs mapped from `data/core_tech.json`. Each slug must be probed alone: a resolved slug returns more than 256 bytes, an unresolved one exactly 256. **Podman has no icon** (nor do zsh, zed or archlinux), so it is skipped rather than rendered blank |
| Learning sub-section | **our own tiles** | `write_learning_icons()` draws them — no icon set carries OCI, LLM, AI-workflow, PKI, tracing or GitOps marks. Each `<img>` carries `title` (name — note) for a hover tooltip and `alt` for assistive tech; the whole section disappears when the list is empty |
| Wave sign-off | **our own card** | `footer.svg` |
| Contribution graph | GitHub | Rendered natively below the README — nothing to do |

**Image paths are repo-relative** (`assets/svg/…`). They resolve in a local preview, in the repo
view, and on the profile page — GitHub renders the profile README with the repository as context.
Absolute `raw.githubusercontent.com` URLs were used at first and 404'd until the repo existed, so
*every* image was broken pre-push; `IMAGE_BASE` in `build_readme.py` switches to absolute in one
constant if that is ever needed.

## Editing

- **Tool list** → `data/core_tech.json`. Names missing from `SKILL_SLUGS` simply don't appear in the
  icon row; add a mapping only after probing that the slug resolves.
- **Learning list** → `data/learning.json`; `icon` must be a key in `GLYPHS`, or add a glyph function.
- **Badge targets** → `SITE`, `LINKEDIN`, `EMAIL` in `build_readme.py` (`USER`, `BRANCH` too).
- **Palette** → the colour constants at the top of `build_readme.py`.
