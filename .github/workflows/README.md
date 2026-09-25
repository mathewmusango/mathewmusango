# Workflows

## Naming

- One purpose per file, named for the task — `checks.yml`, `codeql.yml`. A second file for the same kind of job takes the `{task}-{language|resource}` form.
- Display names are quoted: an unquoted colon+space is invalid YAML.
- The ruleset on `main` is in [`rulesets/`](../../rulesets/README.md); the rest of `.github/` is indexed in [`.github/`](../INDEX.md).
- Branch names are enforced by the `branches: all` ruleset, not by a workflow — a `create:`-triggered check fires only after the ref exists, so it could report but never prevent. See [`rulesets/`](../../rulesets/README.md).

## `checks.yml`

- Pull requests to `main`, plus manual dispatch. One caller job per surface, each calling a reusable workflow in `mathewmusango/my-workflows`, SHA-pinned with the tag in a trailing comment — a bare SHA cannot be bumped by Dependabot.
- Each reusable self-gates on changed files, so an untouched surface skips and reports success.
- A reported name is composed across the reusable boundary as `<caller job key> / <leaf job name>` — which is why moving a job between this file and `security.yml` renamed no context. The five the live ruleset requires are the two below plus the three in `security.yml`; [`rulesets/main.md`](../../rulesets/main.md) holds the record.
- Local parity: [`containers/checks/`](../../containers/checks/README.md), driven by [`scripts/checks/local.sh`](../../scripts/checks/local.sh).

| Caller job | Reusable workflow | Reported check name |
| --- | --- | --- |
| `shell` | `checks-shell.yml` | `shell / shellcheck` |
| `yaml` | `checks-yaml.yml` | `yaml / syntax` · `yaml / actionlint` |

## `security.yml`

- The same shape and the same trigger as `checks.yml` — one caller job per reusable — split by *concern*: these are the security tools rather than the linting surfaces. It keeps the two jobs that read a secret and reach a third party visibly separate, and it is the part the local stack deliberately does **not** mirror.

| Caller job | Reusable workflow | Reported check name |
| --- | --- | --- |
| `secrets` | `security-gitleaks.yml` | `secrets / gitleaks` |
| `gitguardian` | `security-gitguardian.yml` | `gitguardian / gitguardian` — needs the `GITGUARDIAN_API_KEY` secret; **not** a required check |
| `deps` | `security-deps.yml` | `deps / dependency-review` — pull requests only |

## `codeql.yml`

- Push and pull requests to `main`, weekly, and manual dispatch. Matrix: `actions` only, `build-mode: none`, on `security-extended`.
- `security-events: write` + `contents: read` on the job; every action SHA-pinned with a version comment.
- Alerts land in the Security tab and are advisory: the ruleset carries no `code_scanning` rule here, so a finding does not hold up a merge.
