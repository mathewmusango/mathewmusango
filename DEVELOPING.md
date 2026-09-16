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
| `assets/svg/icons/*.svg` | **Generated** Learning glyphs (`cloud`, `chip`, `spark`, `server`, `key`, `chart`, `cube`, `pipeline`) |
| `assets/svg/brands/*.svg` | Hand-kept brand marks the CDN no longer serves — currently just AWS, with its provenance in that folder's README |
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

It prunes Learning glyphs whose entry has been removed, so deleting an item from the list cleans up
after itself.

The page is deliberately just three centred blocks — the badge row, **Languages and Tools**, and
**Learning** — followed by the wave. The `<sub>` note that used to sit under the wave was removed at
the user's request (2026-09-16): with nothing else on the page, it was noise.

Preview: open `README.md` in Zed and *Open Preview* (`ctrl-k v`) — relative image paths resolve
locally, so no push is needed to see the result.

## How the README is assembled

| Piece | Rendered by | Notes |
| --- | --- | --- |
| Contact badges | shields.io | **Static** badges only — no third-party integration that can go stale |
| Languages and tools | Simple Icons CDN, in vendor colours | Each icon is served in the brand's own colour (`cdn.simpleicons.org/<slug>`), mapped from `data/core_tech.json`. **Probe a slug before trusting it — an unknown one answers `404` with a zero-byte body.** A brand colour that would fail WCAG's 3:1 contrast on GitHub's white or dark canvas gets a tint for that theme alone, via `<picture>` + `prefers-color-scheme` (GitHub supports it in READMEs); those tints live in `THEME_COLOURS`, derived from the brand hex by mixing towards black or white. **AWS is no longer in the set** (withdrawn at Amazon's request), so it is committed in the AWS orange at `assets/svg/brands/amazonaws.svg`. Every icon is its own `<img>` with `title` and `alt`, so each has a hover tooltip |
| Learning sub-section | Vendor marks where the subject is a product, our own glyphs where it is an area | `qemu`, `openssl` and `opentelemetry` are real vendor marks (the tools behind those subjects); OCI, local-LLM work, AI-assisted workflows, Terraform modules and GitOps are ours (`cloud`, `chip`, `spark`, `cube`, `pipeline`) because no honest mark exists — Oracle has none in the set, no LLM runtime has been chosen, and Terraform would duplicate the row above. Hover shows `name — note`; the row disappears when the list is empty |
| Wave sign-off | **our own card** | `footer.svg` |
| Contribution graph | GitHub | Rendered natively below the README — nothing to do |

**Image paths are repo-relative** (`assets/svg/…`). They resolve in a local preview, in the repo
view, and on the profile page — GitHub renders the profile README with the repository as context.
Absolute `raw.githubusercontent.com` URLs were used at first and 404'd until the repo existed, so
*every* image was broken pre-push; `IMAGE_BASE` in `build_readme.py` switches to absolute in one
constant if that is ever needed.

## Editing

- **Tool list** → `data/core_tech.json`. A name with no entry in `BRAND_SLUGS` doesn't appear in the row;
  add a mapping only after probing it (`cdn.simpleicons.org/<slug>` → `404` with a zero-byte body means
  it doesn't exist). If the CDN has dropped the mark entirely — as with AWS — commit it under
  `assets/svg/brands/` and list the slug in `LOCAL_BRANDS`.
- **Theme tints** → `THEME_COLOURS`. Only brands whose official colour fails 3:1 contrast belong
  there; re-derive a value by mixing the brand hex 45% towards black (light canvas) or 55% towards
  white (dark canvas, `#0d1117`). An entry gives that icon a `<picture>` swap.
- **Learning list** → `data/learning.json`. Each entry carries either `slug` (a vendor mark) or
  `glyph` (one of ours); unknown keys are skipped, and glyphs no longer referenced are pruned from
  `assets/svg/icons/` on the next build. Glyphs are drawn in the 48-unit box and displayed through
  `GLYPH_VIEW = "6 6 36 36"`, so keep their geometry roughly inside `9…39`.
- **Badge targets** → `SITE`, `LINKEDIN`, `EMAIL` in `build_readme.py` (`USER`, `BRANCH` too).
- **Palette** → the colour constants at the top of `build_readme.py`.
