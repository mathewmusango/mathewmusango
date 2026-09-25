# rulesets — branch protection as code

A ruleset is a repository setting, not a file, so nothing here arrives by clone or pull — the JSON is read back and written in place with `gh api`.

| File | What it is |
| --- | --- |
| [`main.json`](main.json) | the live ruleset on `refs/heads/main`, in GitHub's export/import format |
| [`main.md`](main.md) | the record beside it — what it does and does not enforce, how it was applied, how it was verified |
| [`all.json`](all.json) | the live ruleset on every branch — the branch-name gate |
| [`all.md`](all.md) | the record beside it, in the same shape |

## Naming

`<scope>: <ref pattern>`. The name answers **which ref this gates**; the payload says what the rules are, because those drift.

| Live name | What it gates |
| --- | --- |
| `branch: main` | the default branch — singular, one branch |
| `branches: all` | every branch — the name gate |

The left half is the scope: `branch` when a single branch is gated, `branches` when the ruleset covers all of them. The right half is the ref pattern where there is one. Nothing in GitHub references a ruleset name — unlike a workflow display name, which `workflow_run:` matches — so a name is free to change: one `PUT`, id unchanged.

No tag ruleset: this repository cuts no releases, so `refs/tags/v*` has nothing to protect.
