# container/checks (compose services)

One compose service per check surface, each pinned to a purpose-built tool image and running the **exact command** its CI counterpart runs. The point is parity: a green container here means the same thing as a green CI job.

Declared here, driven by [`scripts/checks/local.sh`](../../scripts/checks/README.md) — the preferred entry point:

```sh
scripts/checks/local.sh yaml-syntax   # diff-gated, the normal way
```

Raw compose, for running one service by hand:

```sh
podman-compose -f container/checks/compose.yml run --rm yaml-syntax
```

## Services

| Service | Image | Runs |
| --- | --- | --- |
| `shell` | `koalaman/shellcheck-alpine` | `shellcheck -S warning` over `*.sh` + `.githooks/` |
| `yaml-actionlint` | `rhysd/actionlint` | `actionlint` over the workflows |
| `yaml-syntax` | `ruby:alpine` | `ruby -ryaml` over every `*.yml` / `*.yaml` |

`secrets` and `deps` have no service here on purpose: `gitleaks` and `dependency-review` are CI-only surfaces, the second because it reads a pull-request diff.

## Notes

- The repo root is mounted at `/repo` **read-only** — no check can modify the tree.
- Images carry mutable `latest` tags on purpose (they track whatever CI uses); the first run pulls them.
- Compose interpolates `$VAR` from the host environment at parse time, so a shell variable inside `command:` must be written `$$`. Getting this wrong empties the loop variables and **silently skips every file**.
- Entrypoints differ per image: `actionlint` runs the tool directly (args only), while the alpine images need an explicit `sh -c`.
- Scans are extension-wide across the whole repo (`.git` pruned), so new files in new locations are never missed.
- Needs podman and `podman-compose` on the host. The GitHub workflows stay the authoritative gate.
