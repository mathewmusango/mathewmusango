# github-profile

My GitHub hub page — a single, self-contained page that shows the public work on
[github.com/mathewmusango](https://github.com/mathewmusango) at a glance: headline stats, a
profile card, tech stack and language mix, the contribution calendar, and the repositories
worth opening first.

The layout follows the dark, green-accented profile-hub design (stat row → profile card +
tech stack → contributions → project cards). It carries no third-party branding, no
analytics, and no runtime requests to any other host.

## Stack

Plain HTML, CSS and JavaScript — no build step, no framework, no package manager, no
dependencies. The page renders from a committed data snapshot, so it works offline, from
`file://`, and on any static host.

Every asset is local, including the avatar, so opening the page makes **zero** requests to
other domains.

## Layout

| Path | What it is |
| --- | --- |
| `index.html` | Page shell — hero copy, panel placeholders, footer |
| `assets/css/style.css` | All styling (dark, GitHub-flavoured, responsive) |
| `assets/js/app.js` | Renders each panel from `window.PROFILE` |
| `assets/img/avatar.png` | Avatar, downloaded by the fetch script |
| `data/profile.json` | Data snapshot — for tooling, diffs and review |
| `data/profile.js` | The same snapshot as `window.PROFILE = {…}`, loaded by `<script src>` |
| `scripts/fetch_profile.py` | Refreshes the snapshot and the avatar from GitHub's public API |
| `.github/workflows/pages.yml` | Publishes the site to GitHub Pages |

`data/profile.js` is loaded with a `<script src>` tag rather than `fetch`ed as JSON: that
keeps the page working straight off the filesystem (`file://`), with no CORS problems and no
extra request.

## Preview locally

Open the file directly — no server needed:

```sh
xdg-open index.html
```

Or serve it if you prefer real URLs:

```sh
python3 -m http.server 8080   # → http://localhost:8080
```

## Refresh the data

```sh
python3 scripts/fetch_profile.py
```

The script uses only **public, unauthenticated** GitHub endpoints, so no token is needed:

- `/users/<user>` — profile, followers, join date
- `/users/<user>/repos` + `/repos/<user>/<repo>/languages` — repositories and language bytes
- `/repos/<user>/<repo>/readme` — fallback description when a repo has none
- `github.com/users/<user>/contributions` — the contribution calendar
- `github.com/<user>.png` — the avatar

It rewrites `data/profile.json`, `data/profile.js` and `assets/img/avatar.png`, then prints
a summary. Commit the result to publish the new numbers.

Three editorial values are set at the top of the script, since the API does not carry them:

```python
CORE_TECH = [...]   # the "Core technologies" chips
COMPANY = ""        # profile-card company row; empty hides the row
MAX_PROJECTS = 8    # how many repos to show, most stars first
```

Columns are derived, not hand-written: `Total repos`, `All stars` and `Followers` come from
the repository list, and `Years active` from the account's creation date.

## Deploy

`.github/workflows/pages.yml` stages `index.html`, `assets/` and `data/` into `_site/` and
publishes them with the official Pages actions on every push to `main` (plus manual
dispatch). Permissions are least-privilege — `pages: write` + `id-token: write`, no
`contents: write` — and runs are serialized on a `pages` concurrency group.

One-time setup, in the repository settings:

1. **Settings → Pages → Build and deployment → Source: GitHub Actions.**
2. Push to `main` — the site lands at `https://<user>.github.io/github-profile/`.

All paths in the page are relative, so it also serves correctly from a root-hosted bucket
(no base path to strip) — relevant if it ever moves to S3/CloudFront.

## Editing

- **Hero copy** — `index.html` (`data-fill="name"` / `data-fill="handle"` spans are
  overwritten with live values at render time; the text in the file is the no-JS fallback).
- **Stat labels, section titles, empty-state text** — `assets/js/app.js`.
- **Colours, spacing, breakpoints** — the custom properties at the top of
  `assets/css/style.css`; the contribution shades use GitHub's dark scale
  (`#161b22 → #0e4429 → #006d32 → #26a641 → #39d353`).

The footer's "as of" date comes from `generated` in the snapshot, so it always matches the
last `fetch_profile.py` run.
