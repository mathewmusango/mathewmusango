# Local brand marks

Glyphs the Simple Icons CDN no longer serves, committed here so the tool row stays complete.

| File | Why it is local |
| --- | --- |
| `amazonaws.svg` | AWS was **withdrawn from Simple Icons** — `cdn.simpleicons.org/amazonaws` (and every variant, including `amazonwebservices`, `aws` and `awslambda`) answers `404`, and the npm releases only carried it up to `simple-icons@11`. The trail is visible in `BRAND_SLUGS` / `LOCAL_BRANDS` in `scripts/build_readme.py`. |

`amazonaws.svg` was taken from `simple-icons@11` and recoloured to the **AWS orange** (`#FF9900`, the
colour Simple Icons used for it) so it sits naturally beside the other vendor-coloured glyphs and
stays legible on both a white and a dark canvas. Path data is unchanged. The mark is Amazon's; it is
used here only to name a tool this profile uses, the same way any tool list would.

Remove `"AWS"` from `data/core_tech.json` to drop it from the row, or replace the file if a better
source appears.
