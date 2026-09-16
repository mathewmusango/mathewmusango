# Local brand marks

Glyphs the Simple Icons CDN no longer serves, committed here so the tool row stays complete.

| File | Why it is local |
| --- | --- |
| `amazonaws.svg` | AWS was **withdrawn from Simple Icons** — `cdn.simpleicons.org/amazonaws` (and every variant) answers `404`, and older npm releases only carried it up to `simple-icons@11`. The trail is visible in `BRAND_SLUGS` / `LOCAL_BRANDS` in `scripts/build_readme.py`. |

`amazonaws.svg` was taken from `simple-icons@11` and **recoloured** to the README's accent
(`#39d353`) so it matches the CDN glyphs next to it — path data unchanged. The mark is Amazon's;
it is used here only to name a tool this profile uses, the same way any tool list would.

Refresh it by hand if a better source appears, or drop `"AWS"` from `data/core_tech.json` to remove
it from the row.
