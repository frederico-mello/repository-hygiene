# Proposal

## Why

SonarCloud rule `python:S1172` (MAJOR) flags the unused function parameter
`version` of `cmd_update` in `src/auditoria_higiene/init.py` (line 66; issue
#1134; Sonar key `AZ-WWK_dOeVxLuflbAoh`). The parameter is the remnant of a
"update configuration to a specific version" feature that was never
implemented: `cmd_update` always regenerates `auditoria.yaml` and
`.github/workflows/repository-hygiene.yml` from the templates bundled with the
installed package. The only caller, the `update` subcommand in
`src/auditoria_higiene/cli.py`, forwards a `--version` option that is parsed
and then silently ignored, so the CLI advertises behavior that does not exist.
Version-targeted update is already recorded as removed: the README "Migration
v0.1 to v0.2" table maps `repository-hygiene update` to `removed`, as required
by the `publish-pypi-v020` capability.

## What Changes

- Remove the `version` parameter from `cmd_update`
  (`src/auditoria_higiene/init.py`), keeping `directory` and `dry_run`
  unchanged.
- In `src/auditoria_higiene/cli.py`, remove the `--version` option of the
  `update` subparser and stop forwarding it to `cmd_update`; replace the
  subcommand help text "Update configuration to a specific version" with a
  description of the real behavior (regenerate `auditoria.yaml` and the
  workflow file from the bundled templates). The global `--version`
  (`action="version"`) of the main parser and of `_run_legacy` is out of scope
  and stays.
- Add one CLI regression test asserting `update --version ...` is rejected, so
  the removed affordance cannot return unnoticed.

Observable difference, limited to one no-op flag: `repository-hygiene update
--version X` used to run while silently ignoring `--version`; it now fails as
an unrecognized argument. Every real usage path (`update`, `update --dry-run`,
`update <directory>`, `install`, `install-skill`, `audit`, legacy mode) is
unchanged.

## Capabilities

### New Capabilities

None. This change introduces no new system behavior.

### Modified Capabilities

None at requirement level. No requirement in `openspec/specs/` covers the
`update` subcommand surface or `update --version` (checked all 15
capabilities), and the flag never implemented behavior: `cmd_update` has no
version selection logic to preserve or change. The change metadata opts out of
specs with `skip_specs: true` on that basis.

## Impact

- Affected files: `src/auditoria_higiene/init.py`,
  `src/auditoria_higiene/cli.py`, `tests_package/test_auditoria_package.py`.
- Users: only scripts passing `update --version` are affected. They currently
  get a silent no-op and will now get a clear usage error, which is the honest
  outcome for a flag that never did anything. No README section,
  `docs/MIGRATION.md`, generated workflow template, or skill template
  references `update --version` (verified).
- Acceptance evidence: the regression test locks the flag rejection; the
  existing `test_cli_update_*` tests lock the preserved behavior; SonarCloud
  re-analysis after merge should close issue #1134 automatically (automated
  sync, outside this change).
- Documentation follow-up decisions: README unchanged, because usage,
  installation, configuration, and migration are unchanged for every documented
  command (`update` usage was never documented there). Layperson guide not
  created: no new user-facing capability or practical consequence to explain.
  Code graph not updated: no graph exists in the repository and the change does
  not alter module structure.
- Residual observation, out of scope: the `update` subcommand itself is offered
  by the CLI but absent from the README usage list. Not required by this fix
  and left for a `documentation-consistency` review.

## Risks

- Low probability, low impact: an external script passing `update --version`
  starts failing. Mitigation: the flag never influenced results, the rejection
  message is the standard argparse usage error, and the README migration table
  already marks version-targeted update as removed. Contingency: if a real
  caller appears, re-add the option as an explicitly deprecated no-op with a
  warning for one release, then remove it.
- Low probability, low impact: the help text change breaks a test that asserts
  exact help wording. Checked: the existing tests only assert that `update`
  appears in help output.
