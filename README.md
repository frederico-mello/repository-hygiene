# repository-hygiene

> **Breaking change: v1.0.0 uses English configuration keys.** See
> [docs/MIGRATION.md](docs/MIGRATION.md) to rename your `auditoria.yaml`.

Audit hygiene for Git repositories. Checks for secrets, broken links,
missing references, untracked artifacts, GitHub Actions workflow security,
and more.

## Installation

```bash
# ephemeral (recommended — no global install)
uvx repository-hygiene install .

# persistent
uv tool install repository-hygiene
# or
pip install repository-hygiene
```

**Note:** after `pip install`, run `repository-hygiene install .` **in the
target repository** to provision configuration, CI workflow, and the
`agent-hygiene-flow` OpenCode skill.

To install directly from GitHub (versions not published on PyPI):

```bash
pip install git+https://github.com/frederico-mello/repository-hygiene.git
```

## Usage

### Initialize repository (`install`)

```bash
repository-hygiene install .             # create auditoria.yaml + workflow + skill
repository-hygiene install --force .     # overwrite existing files
repository-hygiene install --dry-run .   # preview without writing
```

`install` creates:
- `auditoria.yaml` — rule configuration and exceptions
- `.github/workflows/repository-hygiene.yml` — weekly CI workflow
- `.opencode/skills/agent-hygiene-flow/` — OpenCode skill for agents

### Audit

```bash
repository-hygiene .                        # text report (stdout) + JSON (.repository-hygiene/)
repository-hygiene . --format json          # JSON only
repository-hygiene . --format sarif         # SARIF only
repository-hygiene . --output audit.txt     # write to file
```

### Pre-commit hook

```bash
repository-hygiene install --install-hook .   # install hook on first run
```

Blocks commits with `error`-severity findings in staged content. Warnings
(`warning`) are displayed but do not block. To skip:

```bash
git commit --no-verify
```

### Exit codes

| Code | Audit              | Pre-commit hook     |
|------|-------------------|---------------------|
| 0    | clean             | commit allowed      |
| 1    | errors found      | commit blocked      |
| 2    | invalid config    | execution failure   |

## Configuration

`auditoria.yaml` at the repository root:

```yaml
config_version: 1

rules:
  tracked_secrets:
    enabled: true
    severity: error
  broken_internal_links:
    enabled: true
    severity: error
  missing_references:
    enabled: true
    severity: error
  untracked_artifacts:
    enabled: true
    severity: error
  empty_gitkeep_directories:
    enabled: true
    severity: warning
  unreferenced_files:
    enabled: true
    severity: warning
  outdated_documentation:
    enabled: true
    severity: warning
  unintegrated_configurations:
    enabled: true
    severity: warning
  stale_openspec_changes:
    enabled: true
    severity: warning
  insecure_workflows:
    enabled: true
    severity: warning

exceptions:
  tracked_secrets:
    - .secrets.baseline
    - .env.example
  untracked_artifacts:
    - .git
  unreferenced_files:
    - .gitignore
    - Makefile
```

### Rules

| Rule | Severity | Description |
|-------|-----------|-----------|
| `tracked_secrets` | error | Passwords, tokens, and credentials in tracked files |
| `broken_internal_links` | error | Markdown links pointing to missing files |
| `missing_references` | error | References to files that do not exist in the repo |
| `untracked_artifacts` | error | Generated files not covered by `.gitignore` |
| `empty_gitkeep_directories` | warning | Directories containing only `.gitkeep` |
| `unreferenced_files` | warning | Files not referenced by any other file |
| `outdated_documentation` | warning | Documentation referencing nonexistent files |
| `unintegrated_configurations` | warning | Tool config without workflow, command, or docs |
| `stale_openspec_changes` | warning | OpenSpec changes stalled for 30+ days |
| `insecure_workflows` | warning | Excessive permissions, actions without pinned version |

## GitHub Actions

The generated workflow (`repository-hygiene.yml`):

- Runs weekly and on push/PR to relevant paths
- Publishes the report to `$GITHUB_STEP_SUMMARY`
- Creates/updates a consolidated issue with findings (`error`); closes when clean

Minimum permissions:

```yaml
permissions:
  contents: read
  issues: write
  pull-requests: read
```

## Migration v0.1 to v0.2

| Command v0.1 | Equivalent v0.2+ |
|-------------|-------------------|
| `repository-hygiene audit .` | `repository-hygiene .` |
| `repository-hygiene install .` | `repository-hygiene install .` |
| `repository-hygiene update` | removed |

## Development

```bash
uv pip install -e . pytest
uv run pytest tests_package/
```

## License

MIT
