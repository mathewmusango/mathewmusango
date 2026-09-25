# Ruleset: `main` — record

**Status:** 🟢 applied — live on `refs/heads/main` · **Config:** [`main.json`](main.json)

**Purpose.** `main` binds every actor: pull requests only, one approval, squash only, five shared-check contexts, no bypass.

| Field | Value |
| --- | --- |
| Enforcement | `active` |
| Merge methods | `squash` only |
| Approvals | 1 · stale reviews dismissed on push · review threads resolved · an extra approval for unattributed changes |
| Required checks | the five contexts below, strict |
| Bypass actors | none |
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

**Verified.** Read back with `gh api repos/mathewmusango/mathewmusango/rulesets` on 2026-09-23, and re-read 2026-09-25: two rulesets now — this one, and [`branches: all`](all.md) for the branch-name gate. Five required contexts, no bypass actors. A context joins the required set only after a run has reported it, so the set holds what has actually run — `policies / branch` joined on 2026-09-25 and was removed the same day, once it was clear a `create:`-only context can never be satisfied on a branch that is pushed to again. Its `branch-policy.yml` caller was then removed from the repository for the same reason: the `branches: all` gate already refuses a bad name at the push, so the workflow could only ever report after the fact.

**Change flow.** Edit the JSON (export format) → apply it → update this record in the same pull request.
