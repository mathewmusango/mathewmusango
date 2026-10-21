# containers/checks (compose services)

One compose service per check surface, each pinned to a purpose-built tool image and running the **exact command** its CI counterpart runs. The point is parity: a green container here means the same thing as a green CI job.

Declared here, driven by [`scripts/checks/local.sh`](../../scripts/checks/README.md) — the preferred entry point:

```sh
scripts/checks/local.sh yaml-syntax   # diff-gated, the normal way
```

Raw compose, for running one service by hand:

```sh
podman-compose -f containers/checks/compose.yml run --rm yaml-syntax
```

## Services

| Service | Image | Runs |
| --- | --- | --- |
| `shell` | `koalaman/shellcheck-alpine` | `shellcheck -S warning` over `*.sh` + `.githooks/` |
| `yaml` | `rhysd/actionlint` | `actionlint` over the workflows |
| `yaml-syntax` | `ruby:alpine` | `ruby -ryaml` over every `*.yml` / `*.yaml` |
| `gitleaks` | `ghcr.io/gitleaks/gitleaks` | whole-repo secret scan against the default rules plus [`gitleaks.toml`](gitleaks.toml) — history where `.git` is a directory, the working tree here (see below) |

`deps` has no service here on purpose: `dependency-review` reads a pull-request diff.

## Notes

- The repo root is mounted at `/repo` **read-only** — no check can modify the tree.

`gitleaks` is **local only** and **ungated**. CI no longer runs a secrets scan — GitHub secret scanning (with push protection) blocks a credential before the commit lands and GitGuardian reports on every push — but neither can warn you while you work. It is the only surface without a diff gate: a leaked secret has no changed-file set, and the rule set moves independently of the tree. Coverage is whatever the layout allows: in a plain clone `.git` is a directory, so it scans every commit (`git --log-opts=--all`, where `.gitignore` is honoured implicitly); in this checkout `.git` is a *file* pointing at the umbrella's gitdir, which the mount does not include, so history is unreachable and it scans the whole working tree. [`gitleaks.toml`](gitleaks.toml) extends the default rules and allowlists `.preview/`, which is gitignored local preview output rather than repository content.
- Images carry mutable `latest` tags on purpose (they track whatever CI uses); the first run pulls them.
- Compose interpolates `$VAR` from the host environment at parse time, so a shell variable inside `command:` must be written `$$`. Getting this wrong empties the loop variables and **silently skips every file**.
- Entrypoints differ per image: `actionlint` runs the tool directly (args only), while the alpine images need an explicit `sh -c`.
- Scans are extension-wide across the whole repo (`.git` pruned), so new files in new locations are never missed.
- Needs podman and `podman-compose` on the host. The GitHub workflows stay the authoritative gate.
