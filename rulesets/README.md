# rulesets — branch protection as code

A ruleset is a repository setting, not a file, so nothing here arrives by clone or pull — the JSON is read back and written in place with `gh api`.

| File | What it is |
| --- | --- |
| [`main.json`](main.json) | the live ruleset on `refs/heads/main`, in GitHub's export/import format |
| [`main.md`](main.md) | the record beside it — what it does and does not enforce, how it was applied, how it was verified |

One ruleset, and no tag ruleset: this repository cuts no releases, so `refs/tags/v*` has nothing to protect.
