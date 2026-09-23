# .github

Named `INDEX.md`, not `README.md`, on purpose: GitHub renders a `.github/README.md` as the repository's landing page, ahead of the root `README.md`, so a config index under that name would replace this repository's page.

| File | What it is |
| --- | --- |
| [`CODEOWNERS`](CODEOWNERS) | `* @mathewmusango` — one line, no exceptions |
| [`dependabot.yml`](dependabot.yml) | the `github-actions` default, and nothing else — no package manifest here means no ecosystem entry |
| [`workflows/checks.yml`](workflows/checks.yml) | shared checks, one caller job per surface |
| [`workflows/codeql.yml`](workflows/codeql.yml) | CodeQL for `actions` |

The workflows are documented beside them: [`workflows/`](workflows/README.md).

## Security surfaces

Where each one acts, and whether it can hold back a merge.

| Surface | Where it acts | Blocks a merge? |
| --- | --- | --- |
| Push protection | `git push`, before the pull request exists | **Yes** — the push is refused |
| Native secret scanning | the whole repository, every branch | No — an alert in the Security tab |
| `secrets / gitleaks` | CI, on the pull request | No — nothing is required on `main` |
| `deps / dependency-review` | CI, on the pull-request diff | No — nothing is required on `main` |
| CodeQL | the pull request's analysis, and the `main`/weekly baseline | No — the ruleset has no `code_scanning` rule |
| Dependabot alerts | the dependency graph, from the default branch | No — it answers with a patch pull request |

Only the push is blocked today: the live ruleset on `main` carries no required checks, so every CI surface below is advisory. [`rulesets/`](../rulesets/README.md) holds both what it does enforce and the shape it is set out to enforce.

## Settings that are not files

Set by hand; a clone or a pull carries none of them.

| Setting | State |
| --- | --- |
| Rulesets | **live:** `deletion` + `non_fast_forward` only — no pull-request rule and no required checks, so direct pushes are allowed. The target shape — pull requests only, one approval, squash, four required checks, no bypass — is recorded in [`../rulesets/`](../rulesets/README.md) and is **not applied yet** |
| Labels | `dependencies` · `github-actions` — the two `dependabot.yml` names exist |
| Push protection | on |
| Secret scanning | on |
| Private vulnerability reporting | on — hence the **Security → Report a vulnerability** route in [`SECURITY.md`](../SECURITY.md) |
| Non-provider secret patterns | **off** — free here, and the only cover for a secret no provider pattern matches |
| Secret validity checks | **off** — free here, and it separates a live secret from a dead one |
