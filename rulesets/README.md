# rulesets — branch protection as code

| File | What it is |
| --- | --- |
| [`main.json`](main.json) | the live ruleset on `refs/heads/main`, in GitHub's export/import format |
| [`main.md`](main.md) | the record beside it — what it requires, how it was applied |
| [`all.json`](all.json) | the live ruleset on every branch — the branch-name gate |
| [`all.md`](all.md) | the record beside it, in the same shape |

## Naming

`<scope>: <ref pattern>` — the name says **which ref this gates**.

| Live name | What it gates |
| --- | --- |
| `branch: main` | the default branch — singular, one branch |
| `branches: all` | every branch — the name gate |
