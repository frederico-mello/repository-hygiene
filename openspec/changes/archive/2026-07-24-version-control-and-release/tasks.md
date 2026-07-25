## 1. Conventional Commit Audit Rule

- [x] 1.1 Implement `commit_check.py` with `validar_commits(repo_path)` that validates commit messages against Conventional Commits format (types: feat, fix, docs, style, refactor, perf, test, chore, ci, build; optional scope; breaking change `!`), ignores merge commits, handles empty repos and missing git gracefully
- [x] 1.2 Integrate `conventional-commits` rule into `core.py` audit pipeline, consuming config `enabled` (default `true`) and `level` (default `warning`) from `auditoria.yaml`
- [x] 1.3 Add tests for `validar_commits()` — valid messages (all types, with/without scope, breaking change), invalid messages (wrong type, malformed scope, no description), merge commits skipped, empty repo, missing git

## 2. Hook Pre-commit + Init Integration

- [x] 2.1 Create `commit-msg` hook in `src/auditoria_higiene/templates/commit-msg` that validates commit message against Conventional Commits and blocks invalid commits with clear error message
- [x] 2.2 Update `init.py` to install `commit-msg` hook by default on `--init`, preserving existing hooks (warn + skip) unless `--force` is used
- [x] 2.3 Add tests for hook behavior — blocks non-conventional commit, allows conventional commit, preserves existing hook, `--force` overwrites

## 3. Project Documentation & Templates

- [x] 3.1 Verify README contains PyPI install instructions (`pip install repository-hygiene`) and Migration section mapping old CLI commands to current equivalents; update if any reference is stale
- [x] 3.2 Update `AGENTS.md` to document Conventional Commits as mandatory format with list of accepted types
- [x] 3.3 Update workflow template `src/auditoria_higiene/templates/workflow.yml` to reference `repository-hygiene` dynamically instead of hardcoded `repository-hygiene==0.2.0`
- [x] 3.4 Update template snapshot tests to verify no hardcoded version in generated workflow

## 4. Release CI/CD Pipeline

- [x] 4.1 Create `.github/workflows/release.yml` with trigger on push to main, running semantic release analysis, version bump, changelog generation, git tag creation, build via setuptools, and PyPI upload via PYPI_TOKEN
- [x] 4.2 Add `actionlint` validation for the release workflow YAML syntax and structure
- [x] 4.3 Update CHANGELOG.md with release notes for 0.3.0 (initial automated release)
