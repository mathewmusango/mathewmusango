# Workflows

## Naming

- One purpose per file, named for the task — `checks.yml`, `codeql.yml`. A second file for the same kind of job takes the `{task}-{language|resource}` form.
- Display names are quoted: an unquoted colon+space is invalid YAML.
- The ruleset on `main` is in [`rulesets/`](../../rulesets/README.md); the rest of `.github/` is indexed in [`.github/`](../INDEX.md).

## `checks.yml`

- Pull requests to `main`, plus manual dispatch. One caller job per surface, each calling a reusable workflow in `mathewmusango/my-workflows`, SHA-pinned with the tag in a trailing comment — a bare SHA cannot be bumped by Dependabot.
- Each reusable self-gates on changed files, so an untouched surface skips and reports success.
- A reported name is composed across the reusable boundary as `<caller job key> / <leaf job name>`. Nothing is required on `main` yet, so all of these are advisory — [`rulesets/main.md`](../../rulesets/main.md) records the set that is set out to be required.
- Local parity: [`containers/checks/`](../../containers/checks/README.md), driven by [`scripts/checks/local.sh`](../../scripts/checks/local.sh).

| Caller job | Reusable workflow | Reported check name |
| --- | --- | --- |
| `shell` | `checks-shell.yml` | `shell / shellcheck` |
| `yaml` | `checks-yaml.yml` | `yaml / syntax` · `yaml / actionlint` |
| `secrets` | `security-secrets.yml` | `secrets / gitleaks` |
| `deps` | `security-deps.yml` | `deps / dependency-review` — pull requests only |

## `codeql.yml`

- Push and pull requests to `main`, weekly, and manual dispatch. Matrix: `actions` only, `build-mode: none`, on `security-extended`.
- `security-events: write` + `contents: read` on the job; every action SHA-pinned with a version comment.
- Alerts land in the Security tab and are advisory: the ruleset carries no `code_scanning` rule here, so a finding does not hold up a merge.
