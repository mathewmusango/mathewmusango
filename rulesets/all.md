# Ruleset: `branches: all` — record

**Status:** 🟢 applied — live on every branch · **Config:** [`all.json`](all.json)

**Purpose.** The branch-name gate. This plan has no allow-list rule for names: `branch_name_pattern` is rejected by the API (`422 Invalid rule`, with an empty reason) and the UI does not offer "Restrict branch names" either. So the allow-list is expressed the other way round — this ruleset targets **every** branch, *excludes* the names that are allowed, and applies `creation`. Creating anything not excluded is refused at the push.

| Field | Value |
| --- | --- |
| Target | every branch (`~ALL`), minus the excludes below |
| Required checks | none — this gates creation, not merging |
| Bypass actors | none, so the name rules bind everyone, owner included |
| Rules | `creation` only |

**Why exactly one rule.** An all-branches ruleset that also carried `deletion`, `non_fast_forward` or `pull_request` would protect every branch the way `main` is protected — and its `deletion` rule would make a badly named branch **impossible to delete**. The first attempt at this ruleset did exactly that; it had to be disabled to clean up. Deletion and force-push protection belong to `branch: main`.

## The allowed names

The excludes *are* the allow-list:

| Excluded, i.e. allowed | Notes |
| --- | --- |
| `refs/heads/main` | the default branch |
| `refs/heads/dependabot/*` · `/*/*` · `/*/*/*` · `/*/*/*/*` | four levels, so a monorepo branch such as `dependabot/npm_and_yarn/packages/app/foo-1.0.0` is not refused |
| `refs/heads/feature/*` · `fix/*` · `docs/*` · `ci/*` · `infra/*` · `security/*` · `governance/*` · `deps/*` · `content/*` | one path segment each, matching the branch-policy leaf's slug shape |

**`**` does not work here.** GitHub uses `File::FNM_PATHNAME` and does not support `File::FNM_EXTGLOB`, so `*` does not cross `/` and `**` matches **nothing at all** — silently, with no error to warn you. One pattern per level is the consequence.

**What this cannot enforce.** The slug charset, `[a-z0-9]+([._-][a-z0-9]+)*`. Patterns cannot express it, so `ci/Bad_Slug` remains creatable. The `branch-policy.yml` leaf reports that case as `policies / branch` — deliberately **not** a required context, because a `create:`-only check can never be satisfied on a branch that is pushed again (or rebased by Dependabot).

## Applying

```sh
# Read it back — this is how the file here was produced
gh api repos/mathewmusango/mathewmusango/rulesets/24007901

# Replace it in place. Strip id, source and source_type from the body first:
# they are read-only, and the id lives in the URL.
gh api --method PUT repos/mathewmusango/mathewmusango/rulesets/24007901 --input rulesets/all.json
```

**Verified.** Read back 2026-09-25 and probed in the same pass: `bad/probe-again` was **refused** — `GH013: Cannot create ref due to creations being restricted` — while `ci/ruleset-verify` and a four-deep `dependabot/…` branch were **accepted**, then deleted. Earlier probes established the failure modes this file records: `~ALL` is required for the include (a `refs/heads/**` include matches nothing), and `**` in an exclude exempts nothing.

**Change flow.** Edit the JSON (export format) → apply it → update this record in the same pull request.
