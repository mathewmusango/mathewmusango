# Workflows

## Naming

- One purpose per file, named for the task — `checks.yml`, `codeql.yml`. A second file for the same kind of job takes the `{task}-{language|resource}` form.
- Display names are quoted: an unquoted colon+space is invalid YAML.
- The ruleset on `main` is in [`rulesets/`](../../rulesets/README.md); the rest of `.github/` is indexed in [`.github/`](../INDEX.md).

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

## `branch-policy.yml`

- **Trigger:** `create:` only. It holds no logic: one job, `policies`, calls the shared `branch-policy.yml` leaf in `mathewmusango/my-workflows`, at the same SHA-pin and tag comment as `checks.yml`. It reports as `policies / branch` and is **not** a required check.
- **It reports, it does not block.** A `create:`-triggered job fires *after* the ref exists, so the name is already made; `main` and `dependabot/*` pass, and anything else takes a typed prefix — `feature/`, `fix/`, `docs/`, `ci/`, `infra/`, `security/`, `governance/`, `deps/`, `content/` (not `chore/`, not `feat/`).

## `codeql.yml`

- Push and pull requests to `main`, weekly, and manual dispatch. Matrix: `actions` only, `build-mode: none`, on `security-extended`.
- `security-events: write` + `contents: read` on the job; every action SHA-pinned with a version comment.
- Alerts land in the Security tab and are advisory: the ruleset carries no `code_scanning` rule here, so a finding does not hold up a merge.
