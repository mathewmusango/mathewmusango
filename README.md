# my-github-profile

My GitHub hub page — one self-contained page for the public work on
[github.com/mathewmusango](https://github.com/mathewmusango): headline stats, a profile card,
tech stack and language mix, the contribution calendar, and the repositories worth opening
first.

The layout follows the dark, green-accented profile-hub design (hero → stat row → profile card
+ tech stack → contributions → project cards). It carries no third-party branding, no
analytics, and no trackers.

## Stack

Plain HTML, CSS and JavaScript — no build step, no framework, no package manager, no
dependencies. Everything is committed, including the avatar, so the page renders offline and
from `file://`, and can be served by any static host.

## Live data

The stats are **live**, in two layers:

| Layer | What it covers | How fresh |
| --- | --- | --- |
| Client-side | Stats row, profile card, tech stack/languages, project cards | Fetched from `api.github.com` on every page view |
| Snapshot | Everything above **plus the contribution calendar**, which has no public client-side endpoint | Refreshed daily by the scheduled workflow, or by hand |

On load the page paints the committed snapshot immediately — so it is never blank and still
works with JavaScript off — then repaints from GitHub's API when it answers. If the API is
rate-limited or unreachable, the snapshot stays on screen and the footer says so.

Practical details:

- The public API allows **60 anonymous requests/hour per IP**; a full load uses ~10 (profile,
  repos, then per-repo language bytes). Results are cached in `localStorage` for 10 minutes so
  a refresh or a second visit costs nothing.
- The avatar stays the **locally committed** copy rather than the CDN URL, so no visitor
  request ever leaves for another host.
- Live fetching does mean visitors' browsers talk to `api.github.com` (as they would for any
  card service). Set `LIVE = false` in `assets/js/app.js` to serve the snapshot only — the page
  then makes **zero** external requests.

## Preview locally

Open the file directly — no server needed:

```sh
xdg-open index.html
```

Or serve it if you prefer real URLs:

```sh
python3 -m http.server 8080   # → http://localhost:8080
```

## Refresh the snapshot

```sh
python3 scripts/fetch_profile.py
```

Public, **unauthenticated** endpoints only, so no token is needed:

- `/users/<user>` — profile, followers, join date
- `/users/<user>/repos` + `/repos/<user>/<repo>/languages` — repositories and language bytes
- `/repos/<user>/<repo>/readme` — fallback description when a repo has none
- `github.com/users/<user>/contributions` — the contribution calendar
- `github.com/<user>.png` — the avatar

It rewrites `data/profile.json`, `data/profile.js` and `assets/img/avatar.{png,jpg}` (whichever
format GitHub served — the snapshot records the real path), then prints a summary. Commit the
result, or let the scheduled workflow do it daily.

Three editorial values sit at the top of the script, since the API does not carry them:

```python
CORE_TECH = [...]   # the "Core technologies" chips
COMPANY = ""        # profile-card company row; empty hides the row
MAX_PROJECTS = 8    # how many repos to show, most stars first
```

`Total repos`, `All stars` and `Followers` are derived from the repository list; `Years active`
from the account's creation date.

## Layout

| Path | What it is |
| --- | --- |
| `index.html` | Page shell — hero copy, panel placeholders, footer |
| `assets/css/style.css` | All styling (dark, GitHub-flavoured, responsive) |
| `assets/js/app.js` | Paints every panel, then refreshes it from the live API |
| `assets/img/avatar.*` | Avatar, downloaded by the fetch script |
| `data/profile.json` | Data snapshot — for tooling, diffs and review |
| `data/profile.js` | The same snapshot as `window.PROFILE = {…}`, loaded by `<script src>` |
| `scripts/fetch_profile.py` | Refreshes the snapshot and the avatar |
| `.github/workflows/deploy-pages.yml` | Daily snapshot refresh + GitHub Pages publish |

The snapshot is loaded with a `<script src>` tag rather than `fetch`ed as JSON: that keeps the
page working straight off the filesystem, with no CORS problems and no extra request.

## Deploy

`deploy-pages.yml` has two jobs:

- **`refresh`** (schedule + manual only) — runs `fetch_profile.py` and commits the snapshot if
  anything moved. It holds `contents: write` for that one job.
- **`deploy`** — stages `index.html`, `assets/` and `data/` into `_site/` and publishes them
  with the official Pages actions. Least privilege (`pages: write` + `id-token: write`, no
  `contents: write`), serialized on a `pages` concurrency group, and it checks out
  `ref_name` so a scheduled run deploys the snapshot the refresh job just pushed.

One-time setup: **Settings → Pages → Build and deployment → Source: GitHub Actions**, then push
to `main`. The site lands at `https://<user>.github.io/my-github-profile/`.

All paths are relative, so the same files also serve correctly from a root-hosted bucket (no
base path to strip).

### Private repository?

**GitHub Pages cannot serve a private repository on the Free plan.** Per GitHub's docs: *"GitHub
Pages is available in public repositories with GitHub Free and GitHub Free for organizations,
and in public and private repositories with GitHub Pro, GitHub Team, GitHub Enterprise Cloud,
and GitHub Enterprise Server."* — and even then, a Pages site is served **publicly** on the
internet, regardless of repository visibility (only Enterprise Cloud can restrict access).

So the choices are:

| Goal | Way |
| --- | --- |
| A page linked from my GitHub profile | Public repo + Pages (the workflow here, no changes needed) |
| Keep the repo source private, page public | Private repo **+ a paid plan** for Pages — or keep it public and accept that these few files are public anyway |
| Keep everything private | Don't publish: private repo, no Pages job, and either preview locally or host the static files on your own private bucket (S3 + CloudFront, OAC) instead of Pages |

Repository visibility changes nothing else: the fetch uses public endpoints, so the script,
the scheduled refresh and the page all behave identically either way. Dropping the `deploy`
job (or the whole workflow) is all it takes to stop publishing.

## Editing

- **Hero copy** — `index.html` (`data-fill="name"` / `data-fill="handle"` spans are overwritten
  at paint time; the text in the file is the no-JS fallback).
- **Stat labels, section titles, empty-state text** — `assets/js/app.js`.
- **Colours, spacing, breakpoints** — the custom properties at the top of
  `assets/css/style.css`; the contribution shades use GitHub's dark scale
  (`#161b22 → #0e4429 → #006d32 → #26a641 → #39d353`).

The footer's snapshot date comes from `generated` in the snapshot, so it always matches the
last `fetch_profile.py` run.
