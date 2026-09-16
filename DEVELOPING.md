# mathewmusango — profile repo

One snapshot of GitHub's public API feeds **two surfaces**:

| Surface | Files | Where it shows |
| --- | --- | --- |
| **Profile view** — the point of this repo | `README.md` + `assets/svg/*.svg` | The top of <https://github.com/mathewmusango> — GitHub renders the root `README.md` there |
| **Hub page** — a standalone page | `index.html`, `assets/css/`, `assets/js/`, `assets/img/` | Any static host; `deploy-pages.yml` publishes it to GitHub Pages |

Everything on both surfaces comes from `data/profile.json`, a committed snapshot of GitHub's
public API. The design follows the dark, green-accented profile-hub layout (hero → stat row →
tech stack → projects); CheckMyGit's branding from the reference is deliberately absent, as is
any third-party script or card service.

## What GitHub requires for the profile view

GitHub renders this README on the profile page only when **all** of these hold
([docs](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/customizing-your-profile/managing-your-profile-readme)):

- the repository is named exactly like the account — `mathewmusango`;
- **the repository is public** — making it private removes the profile view;
- `README.md` exists at the repository root and is not empty.

So while the profile view is wanted, this repo cannot be private.

## Why the cards are SVG images

A profile page accepts markdown and a sanitised subset of HTML — no CSS, no `<style>`, no
scripts, no classes. The dark cards are therefore drawn as SVG at build time and committed, then
embedded as images with `<img width="100%">`. That keeps the reference design's look (cards,
green accents, language bars) without depending on a third-party card service that could
disappear, rate-limit, or track visitors.

Text is positioned with an approximate Helvetica metric table in `build_readme.py`, so headings
and the tagline can be centred and wrapped without pulling in a font library. Typefaces resolve
in the visitor's browser, so nothing is embedded.

The contribution graph needs no work at all: GitHub renders its own contribution activity
directly below the profile README.

## Layout

| Path | What it is |
| --- | --- |
| `README.md` | **Generated** profile view — edit `scripts/build_readme.py`, not this file |
| `assets/svg/hero.svg` | **Generated** banner — handle pill, name, tagline |
| `assets/svg/stats.svg` | **Generated** four-cell stat row |
| `assets/svg/tech.svg` | **Generated** core technologies + language bars |
| `index.html` | Hub page shell — hero copy, panel placeholders, footer |
| `assets/css/style.css` | Hub page styling (dark, GitHub-flavoured, responsive) |
| `assets/js/app.js` | Hub page renderer — snapshot first, then live API |
| `assets/img/avatar.*` | Avatar, downloaded by the fetch script |
| `data/profile.json` | Snapshot — for tooling, diffs and review |
| `data/profile.js` | The same snapshot as `window.PROFILE = {…}`, loaded by `<script src>` |
| `scripts/fetch_profile.py` | Refreshes the snapshot and the avatar from GitHub's public API |
| `scripts/build_readme.py` | Renders the profile README and the three SVG cards |
| `.github/workflows/deploy-pages.yml` | Daily refresh + GitHub Pages publish |
| `DEVELOPING.md` | This file |

The snapshot is loaded with a `<script src>` tag rather than `fetch`ed as JSON: that keeps the
hub page working straight off the filesystem, with no CORS problems and no extra request.

## Refresh

```sh
python3 scripts/fetch_profile.py && python3 scripts/build_readme.py
```

`fetch_profile.py` uses only public, **unauthenticated** endpoints, so no token is needed:

- `/users/<user>` — profile, followers, join date
- `/users/<user>/repos` + `/repos/<user>/<repo>/languages` — repositories and language bytes
- `/repos/<user>/<repo>/readme` — fallback description when a repo has none
- `github.com/users/<user>/contributions` — the contribution calendar
- `github.com/<user>.png` — the avatar

`build_readme.py` turns that snapshot into `README.md` and the three cards. Editorial values,
since the API does not carry them:

| Where | Constants |
| --- | --- |
| `fetch_profile.py` | `CORE_TECH` (chips), `COMPANY` (empty hides the row), `MAX_PROJECTS` |
| `build_readme.py` | `USER`, `BRANCH`, `RAW` (image base), `SITE`, `LINKEDIN`, `EMAIL`, `GREEN*` palette |
| `assets/js/app.js` | `MAX_PROJECTS`, `MAX_LANGUAGE_REPOS`, `LIVE` |

The daily workflow runs both scripts and commits whatever moved, so the cards — and the
"last refreshed" line — stay current without a third-party service.

## Live data (hub page)

The hub page's numbers are live in two layers:

| Layer | Covers | Freshness |
| --- | --- | --- |
| Client-side | Stats row, profile card, tech stack, project cards | Fetched from `api.github.com` on every page view |
| Snapshot | Everything above **plus the contribution calendar** (no public client-side endpoint) | Daily by the workflow, or by hand |

The snapshot is painted first — so the page is never blank and works with JavaScript off — then
replaced by live data when the API answers. The public API allows **60 anonymous requests/hour
per IP** (a full load costs ~10), so the payload is cached in `localStorage` for 10 minutes; if
the API is rate-limited or unreachable the snapshot stays up and the footer says so. Set
`LIVE = false` in `assets/js/app.js` to serve the snapshot only — the page then makes zero
external requests. The avatar stays the locally committed copy rather than a CDN URL.

## Preview

```sh
xdg-open index.html          # hub page; snapshot loads via <script src>, so file:// works
python3 -m http.server 8080  # or serve it for real URLs
```

The profile view can only be previewed by pushing (or pasting the markdown into a GitHub
comment box, which renders the same subset).

## Deploy

`deploy-pages.yml` has two jobs:

- **`refresh`** (schedule + manual only) — runs both scripts and commits the snapshot, the avatar,
  the cards and the README. It holds `contents: write` for that one job.
- **`deploy`** — stages `index.html`, `assets/` and `data/` into `_site/` (leaving the README
  cards out) and publishes with the official Pages actions. Least privilege (`pages: write` +
  `id-token: write`), serialized on a `pages` concurrency group, and it checks out `ref_name` so
  a scheduled run deploys the commit the refresh job just pushed.

One-time setup: create the public repository `mathewmusango/mathewmusango`, then **Settings →
Pages → Build and deployment → Source: GitHub Actions**. The hub page lands at
`https://mathewmusango.github.io/mathewmusango/`; the profile view appears automatically at
`https://github.com/mathewmusango`.

All hub-page paths are relative, so the same files also serve correctly from a root-hosted
bucket (no base path to strip).

### Private repository?

Not while the profile view is wanted — see [above](#what-github-requires-for-the-profile-view).
Repository visibility is the only lever: drop the profile view and the repo may be private, but
then GitHub Pages can't publish it either on the Free plan (*"GitHub Pages is available in public
repositories with GitHub Free … and in public and private repositories with GitHub Pro, GitHub
Team, GitHub Enterprise Cloud, and GitHub Enterprise Server"*). The hub page is plain static
files, so a private S3 + CloudFront bucket is the alternative if it ever needs to move.
