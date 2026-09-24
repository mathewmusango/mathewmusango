# scripts/checks (local check driver)

[`local.sh`](local.sh) runs the same checks CI runs, on this machine, before a push, and it is what the pre-commit hook execs.

```sh
scripts/checks/local.sh              # every surface whose files changed
scripts/checks/local.sh --full       # every surface, whole repository
scripts/checks/local.sh --full -v    # …and list the files each surface scans
scripts/checks/local.sh shell        # selected surfaces only
```

Diff-gated by default: changed files come from `origin/main...HEAD` plus the staged and unstaged working tree, and a surface with no matching files **skips** rather than runs — the same skip-model CI uses. Each selected surface runs as a service from [`containers/checks/`](../../containers/checks/README.md), where the images and commands are declared. The exit code is 0 only if every surface that ran passed.

**Why this folder is committed** when the rest of `scripts/` is not: `.gitignore` ships only what the page renders, and the local check stack is the one toolchain that has to travel with the repository. `scripts/checks/` is carved out of that allowlist for it; the generator stays local.

## Surfaces

| Surface | Checks | Locally, without a container |
| --- | --- | --- |
| `shell` | `shellcheck -S warning` across `*.sh` and `.githooks/` | `shellcheck -S warning <files>` |
| `yaml-actionlint` | `actionlint` across `.github/workflows/` | `actionlint` |
| `yaml-syntax` | every `*.yml` / `*.yaml` parses | `ruby -ryaml -e 'YAML.load_file(ARGV[0])' <file>` |

The third column is a convenience, not a proof: it uses the host's tool versions rather than the container's, so a pass there says nothing about CI.

## Pre-commit hook

[`.githooks/pre-commit`](../../.githooks/pre-commit) is a five-line shim that execs this driver. Enable it once per clone:

```sh
git config core.hooksPath .githooks
```

It runs through podman, never host tools. Bypass it deliberately with `git commit --no-verify` — CI still runs the full set.

> [!NOTE]
> `.githooks/` holds shell scripts only. The `shell` surface matches everything under that directory, so the hook has no README of its own and is documented here instead.

> [!WARNING]
> A README or any other non-shell file under `.githooks/` makes `shellcheck` fail.
