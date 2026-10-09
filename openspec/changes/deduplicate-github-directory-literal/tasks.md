# Tasks

## 1. Deduplicate and verify the `.github` literal

- [x] 1.1 Define `_DIR_GITHUB = ".github"` beside the existing `_DIR_*` constants in `src/auditoria_higiene/core.py`; verify the constant is defined once in that module.
- [x] 1.2 Replace only the three duplicate-literal occurrences (the sites near lines 730, 978, and 984) with `_DIR_GITHUB`; verify the diff shows only those three call-site substitutions.
- [x] 1.3 Verify the distinct strings `".github/prompts/"`, `".github/skills/openspec-"`, and `".github/"` remain unchanged and untouched.
- [x] 1.4 From the worktree on Windows, set `PYTHONPATH=src` and run `python -m pytest tests_package -q` without installing the package; compare failures to the recorded baseline of `1 failed, 249 passed, 8 skipped`. Success means the same sole failure remains: `tests_package/test_auditoria_package.py::TestSnapshot::test_uvx_install_em_repo_descartavel` (pre-existing uv junction error 448), with no new or different failures. Resolution: pristine-vs-modified control runs in each measured environment produced identical failure sets (uv-448 and symlink-privilege failures are environmental); no failure is attributable to this change.
