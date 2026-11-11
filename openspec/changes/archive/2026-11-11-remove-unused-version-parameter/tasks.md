# Tasks

## 1. Remove the dead `version` parameter and flag

- [x] 1.1 In `src/auditoria_higiene/init.py`, remove `version=None` from the
  `cmd_update` signature (line 66), keeping `directory` and `dry_run`. Verify
  the function body never referenced `version` and that the only caller is
  `src/auditoria_higiene/cli.py`.
- [x] 1.2 In `src/auditoria_higiene/cli.py`, remove the `--version` option of
  the `update` subparser (lines 196-197) and change the dispatch (line 213) to
  `cmd_update(args.directory, dry_run=args.dry_run)`. Replace the subparser
  help `"Update configuration to a specific version"` with an accurate
  one-line description that does not mention a target version (suggestion:
  `"Regenerate configuration and workflow from the bundled templates"`).
  Keep the main parser's `--version` (`action="version"`) and `_run_legacy`
  untouched.
- [x] 1.3 In `tests_package/test_auditoria_package.py`, add
  `test_cli_update_rejeita_flag_version` beside `test_cli_update_dry_run`: run
  `[sys.executable, "-m", "auditoria_higiene.cli", "update", "--version",
  "1.0", "--dry-run", str(tmp_path)]` and assert exit code 2 and that nothing
  was written under `tmp_path`.

## 2. Verify preserved behavior

- [x] 2.1 Baseline on the pre-change state: from the worktree root on Windows
  run `uv run --no-project --with pytest --with-editable . python -m pytest
  tests_package -q` and record the summary line. Baseline recorded while
  planning this change (2026-11-11, Windows, command above): `7 failed, 248
  passed, 3 skipped in 65.00s`. The 7 failures are pre-existing and unrelated
  to this change: 5 `TestDestinoSymlinkExterno` tests in
  `tests_package/test_install_skill.py` (Windows symlink privilege) and 2
  tests in `tests_package/test_mira_partial_gate.py` (their parser expects
  `mira-routing-status.json` under `RUNNER_TEMP` and it is not generated). The
  raw `PYTHONPATH=src` variant without an installed distribution cannot
  collect tests because `auditoria_higiene.__init__` reads
  `importlib.metadata.version("repository-hygiene")`).
- [x] 2.2 Run the same command after the change. Success means the failure set
  is identical to the recorded baseline (same pre-existing environmental
  failures, nothing new) and the new `test_cli_update_rejeita_flag_version`
  passes. Any new or different failure blocks completion.
- [x] 2.3 Smoke the CLI surface:
  `python -m auditoria_higiene.cli update --dry-run <tmp>` exits 0 and prints
  `dry-run` lines; `python -m auditoria_higiene.cli update --help` no longer
  lists `--version` and no longer mentions a target version;
  `python -m auditoria_higiene.cli --version` still prints
  `repository-hygiene <version>`.
- [x] 2.4 Confirm the finding target is gone: `cmd_update` has no `version`
  parameter anywhere in its definition or call sites, and the diff touches
  only `src/auditoria_higiene/init.py`, `src/auditoria_higiene/cli.py`, and
  `tests_package/test_auditoria_package.py`.
- [x] 2.5 Commit with Conventional Commits (suggestion:
  `fix: remove unused cmd_update version parameter and dead update --version flag (python:S1172)`).
