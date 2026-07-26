## 1. Localizer validator reaches the user

- [x] 1.1 Add `_PT_TO_EN`, `_LOCALIZED_CONFIG_KEYS`, and `_validar_chave_localizada` to `src/auditoria_higiene/core.py`
- [x] 1.2 Wire `_validar_chave_localizada` into `carregar_configuracao()` directly after `yaml.safe_load` and before existing validation
- [x] 1.3 Make the validator raise a single configuration error that lists every offending Portuguese key with its English equivalent and points to `docs/MIGRATION.md`
- [x] 1.4 Add the unknown-English-key branch that suggests the closest valid key when edit distance is small enough
- [x] 1.5 Add a Portuguese-keyed fixture at `tests_package/fixtures/auditoria.pt.yaml`
- [x] 1.6 Add parametric unit tests in `tests_package/test_core_localization.py` covering Portuguese-only, mixed Portuguese+English, unknown-English, and unknown-English-with-no-close-match inputs
- [x] 1.7 Verify by running the CLI against the fixture directory: a single English error names every offending key and points to `docs/MIGRATION.md`

## 2. Default config and workflow templates use English identifiers

- [x] 2.1 Translate keys and values in `src/auditoria_higiene/templates/auditoria.yaml` to English using the canonical mapping
- [x] 2.2 Translate job names and step names in `src/auditoria_higiene/templates/workflow.yml` to English
- [x] 2.3 Add a CI assertion that every key in `templates/auditoria.yaml` belongs to the set of valid English configuration keys
- [x] 2.4 Verify by running `repository-hygiene install .` on a scratch directory: the generated `auditoria.yaml` and `repository-hygiene.yml` are in English

## 3. CLI help, errors, and text report are English

- [x] 3.1 Translate `argparse` `description=`, `help=`, and `epilog=` strings in `src/auditoria_higiene/cli.py`
- [x] 3.2 Translate `cmd_*` user-visible error-message strings in `src/auditoria_higiene/cli.py`
- [x] 3.3 Translate user-visible exception messages in `core.py` for public-API entry points (`carregar_configuracao`, audit entry points, `cmd_install`, `cmd_update`); leave internal helper exceptions in their source locale
- [x] 3.4 Translate text-section strings in `src/auditoria_higiene/reporters.py` (`gerar_relatorio_texto`, `gerar_resumo`)
- [x] 3.5 Add a snapshot test in `tests_package/test_reporters.py` that pins the English text output
- [x] 3.6 Add a contract test asserting JSON output shape is unchanged from previous schema versions
- [x] 3.7 Add a contract test asserting SARIF output remains schema-valid
- [x] 3.8 Verify by running `repository-hygiene --help` and an audit with `--format text`: no Portuguese strings reach the user-visible surface

## 4. README, docs, skill, and code docstrings migrate to English

- [x] 4.1 Hand-translate `README.md` to English; leave a top-of-file link to `docs/MIGRATION.md` to be wired in after task 5.1 lands
- [x] 4.2 Hand-translate files under `docs/` to English, excluding `docs/MIGRATION.md`
- [x] 4.3 Hand-translate the body of `src/auditoria_higiene/templates/skills/agent-hygiene-flow/SKILL.md`
- [x] 4.4 Hand-translate Python docstrings across `src/auditoria_higiene/*.py`
- [x] 4.5 Add a CI docstring scan that rejects common Portuguese tokens outside an allowlist for identifier names
- [x] 4.6 Verify by opening `README.md`, a sample docstring, and the skill body: visible content is English; the docstring scan passes

## 5. Migration guide and drift guards

- [x] 5.1 Author `docs/MIGRATION.md` with the canonical Portuguese-to-English key table from `_PT_TO_EN`
- [x] 5.2 Add a CI drift guard asserting `set(_PT_TO_EN.values())` is a subset of the set of valid English configuration keys
- [x] 5.3 Add a CI drift guard asserting the set of Portuguese keys listed in `docs/MIGRATION.md` equals `set(_PT_TO_EN.keys())`
- [x] 5.4 Verify by adding a Portuguese identifier to `_PT_TO_EN` without updating `docs/MIGRATION.md`: the table-drift guard fails. Then verify adding an English-only key with no Portuguese counterpart requires no `MIGRATION.md` row and the guards still pass

## 6. Version 1.0.0 bump, self-audit gate, and cross-repo companion PR

- [x] 6.1 Bump the version in `pyproject.toml` from the current value to `1.0.0`
- [x] 6.2 Add a `BREAKING CHANGE` entry to `CHANGELOG.md` (or `docs/RELEASES.md`) pointing to `docs/MIGRATION.md`
- [x] 6.3 Run `repository-hygiene .` against this repository and resolve findings so the run exits clean
- [x] 6.4 Open a companion PR on `frederico-mello/quiz` that renames Portuguese keys to English in `auditoria.yaml` and bumps the workflow pip pin from `0.2.0` to `1.0.0`
- [x] 6.5 Merge the companion PR before or alongside the `1.0.0` tag; publish to PyPI only after the companion lands
- [x] 6.6 Verify by reading `pyproject.toml` (version shows `1.0.0`), confirming the companion PR is merged on `quiz`, and confirming the self-audit run exits 0
