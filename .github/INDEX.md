# .github

| File | What it is |
| --- | --- |
| [`CODEOWNERS`](CODEOWNERS) | `* @mathewmusango` — one line, no exceptions |
| [`dependabot.yml`](dependabot.yml) | the `github-actions` default, and nothing else — no package manifest here means no ecosystem entry |
| [`ISSUE_TEMPLATE/`](ISSUE_TEMPLATE/) | the issue forms — bug report · feature request · chore, and the contact config |
| [`workflows/checks.yml`](workflows/checks.yml) | shared checks, one caller job per surface |
| [`workflows/security.yml`](workflows/security.yml) | the secret scanners — `secrets`, `deps` — split from `checks.yml` |
| [`workflows/codeql.yml`](workflows/codeql.yml) | CodeQL for `actions` |
