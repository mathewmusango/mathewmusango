# Ruleset: `main` — record

**Status:** 🟢 applied — live on `refs/heads/main` · **Config:** [`main.json`](main.json)

**Purpose.** `main` binds every actor: pull requests only, one approval, squash only, five shared-check contexts, no bypass.

| Field | Value |
| --- | --- |
| Enforcement | `active` |
| Merge methods | `squash` only |
| Approvals | 1 · stale reviews dismissed on push · review threads resolved · an extra approval for unattributed changes |
| Bypass actors | none |
| Required checks | the five below, strict |
| Also | `creation` · `deletion` · `non_fast_forward` · `required_signatures` · `code_scanning` (`high_or_higher`, analysis `errors`) |

## The required contexts

| Context | Comes from |
| --- | --- |
| `shell / shellcheck` | the `shell` caller job |
| `yaml / syntax` | the `yaml` caller job |
| `yaml / actionlint` | the `yaml` caller job |
| `secrets / gitleaks` | the `secrets` caller job |
| `deps / dependency-review` | the `deps` caller job — reports on pull requests only |

## Applying

```sh
# Read it back — this is how the file here was produced
gh api repos/mathewmusango/mathewmusango/rulesets

# Replace it in place. Strip id, source and source_type from the body first:
# they are read-only, and the id lives in the URL.
gh api --method PUT repos/mathewmusango/mathewmusango/rulesets/23608725 --input rulesets/main.json
```
