# .github

| File | What it is |
| --- | --- |
| [`CODEOWNERS`](CODEOWNERS) | `* @mathewmusango` — one line, no exceptions |
| [`dependabot.yml`](dependabot.yml) | the `github-actions` default, and nothing else — no package manifest here means no ecosystem entry |
| [`workflows/checks.yml`](workflows/checks.yml) | shared checks, one caller job per surface |
| [`workflows/security.yml`](workflows/security.yml) | the secret scanners — `secrets`, `gitguardian`, `deps` — split from `checks.yml` |
| [`workflows/branch-policy.yml`](workflows/branch-policy.yml) | the branch-name policy, reported from a `create:` trigger as `policies / branch` |
| [`workflows/codeql.yml`](workflows/codeql.yml) | CodeQL for `actions` |

The workflows are documented beside them: [`workflows/`](workflows/README.md).

## Security surfaces

Where each one acts, and whether it can hold back a merge.

| Surface | Where it acts | Blocks a merge? |
| --- | --- | --- |
| Push protection | `git push`, before the pull request exists | **Yes** — the push is refused |
| Native secret scanning | the whole repository, every branch | No — an alert in the Security tab |
| `secrets / gitleaks` | CI, on the pull request — a required context | **Yes** |
| `gitguardian / gitguardian` | CI, on the pull request — its own caller job and the `GITGUARDIAN_API_KEY` secret | No — it reports; it is not a required context |
| `deps / dependency-review` | CI, on the pull-request diff — a required context | **Yes** |
| `Analyze (…)` + the `code_scanning` rule | the pull request's analysis, and the `main`/weekly baseline | **Yes** — on alerts at `high_or_higher` |
| Dependabot alerts | the dependency graph, from the default branch | No — it answers with a patch pull request |

**Nothing above is advisory.** The live ruleset on `main` requires the five contexts the two caller files report — `shell / shellcheck` · `yaml / syntax` · `yaml / actionlint` · `secrets / gitleaks` · `deps / dependency-review` — so a merge is gated on them, and `code_scanning` blocks a pull request carrying an alert at `high_or_higher`. [`rulesets/`](../rulesets/README.md) holds the record.

## Settings that are not files

Set by hand; a clone or a pull carries none of them.

| Setting | State |
| --- | --- |
| Rulesets | **applied** — `branch: main` (id `23608725`, active): `pull_request` (one approval, squash only, stale reviews dismissed, threads resolved), `required_status_checks` ×5, `required_signatures`, `code_scanning`, `creation` · `deletion` · `non_fast_forward`, and `bypass_actors: []`. Recorded in [`../rulesets/`](../rulesets/README.md) |
| Labels | `dependencies` · `github-actions` — the two `dependabot.yml` names exist |
| Push protection | on |
| Secret scanning | on |
| Private vulnerability reporting | on — hence the **Security → Report a vulnerability** route in [`SECURITY.md`](../SECURITY.md) |
| Non-provider secret patterns | **off** — free here, and the only cover for a secret no provider pattern matches |
| Secret validity checks | **off** — free here, and it separates a live secret from a dead one |
