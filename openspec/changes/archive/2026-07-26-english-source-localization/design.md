## Context

`auditoria-higiene` ships in two locales at once. The package itself — PyPI name `repository-hygiene`, project description, workflow YAML job and step names, CLI behavior — is English. The consumer-facing config schema (`auditoria.yaml` keys), default rendered templates (`templates/auditoria.yaml`, `templates/workflow.yml`), CLI strings, README, docs, and code docstrings are Portuguese. Review bots (`revisor-de-codigo-mira` on `frederico-mello/quiz` PR #59) flag the inconsistency at first import; every new external consumer negotiates two conventions.

The recent PR 59 in `frederico-mello/quiz` copied our Portuguese-keyed config and was immediately flagged — this is the productionized form of the friction this change exists to remove.

The constraint that frames every decision: ship `1.0.0` as a hard break — no Portuguese back-compat, no shim layer, no alias keys. Consumers run `repository-hygiene` against a renamed English config or load fails.

## Goals / Non-Goals

**Goals**
- Single canonical locale: English, across config schema, CLI, default templates, docs, skill, code docstrings.
- Loud failure at config-load time when a Portuguese-keyed `auditoria.yaml` is offered, with a machine-actionable error pointing to `docs/MIGRATION.md`.
- Self-contained design: zero new external libraries; zero new top-level directories.
- Self-audit gate: the change ships with `repository-hygiene . --format text` clean against its own repository.

**Non-Goals**
- No i18n framework, no message catalog, no locale negotiation.
- No PT-key aliases, no transitional release (`0.6` accepts both / `0.7` warns / `1.0` rejects): hard break `1.0.0`.
- No automated translation tooling; surfaces are hand-translated.
- No package rename (`repository-hygiene` is already English).
- No audit-rule behavior changes — only identifiers, message text, and locales move.
- No schema grammar formalization (JSON Schema / pydantic / dataclasses): dictionary validation via explicit key lists only.
- Per proposal non-goals: out-of-tree reformatting (JSON/SARIF output labels, **internal log strings**, error stack traces) stays in the source locale. Only consumer-facing surfaces migrate.

## Decisions

### D1. Static PT→EN dictionary drives load-time validation

`core.py` exposes a module-level immutable `_PT_TO_EN: dict[str, str]` and `_LOCALIZED_CONFIG_KEYS: frozenset[str]`. Both are populated at import time and never mutated. A `_validar_chave_localizada(config: dict) -> None` function compares the loaded config keys against the PT dictionary and the EN allow-list in a single pass, raising `ConfigError` with one consolidated message listing every offending key + its EN equivalent + path to `docs/MIGRATION.md`.

Rationale: dictionary-driven validation ships in one screen of code, requires no new dependency, and survives rule-key additions because the test scaffold (Section 5 in the proposal-aligned risks table) asserts every EN identifier in the dictionary is also a valid config key — so the dictionary cannot suggest an identifier that does not exist.

### D2. Pre-validation runs before audit preparation

`_validar_chave_localizada(config)` is invoked inside `carregar_configuracao()` directly after `yaml.safe_load` and before any consumer of the config dict. Failure is fail-fast and atomic: no partial config consumed.

### D3. String-literal migration without extraction

User-facing Portuguese string literals in `cli.py`, `core.py`, `reporters.py`, and argparse `description=` / `help=` / `epilog=` are replaced with English literals. Internal log strings and stack-trace messages stay in their current locale per the proposal's out-of-scope boundary; the change touches only what an end-user or external CI consumer can observe. No message catalog, no `_()` indirection, no `.mo` / `.po` files.

### D4. Templates carry the new default; install/update logic unchanged

`src/auditoria_higiene/templates/auditoria.yaml` and `templates/workflow.yml` are rewritten with English keys/values. `cmd_install` and `cmd_update` (`init.py`) keep their current `shutil.copy`-based logic — templates are static data, and install/update picks up the new content automatically.

### D5. Cross-repo companion PR on `frederico-mello/quiz`

`quiz`'s PR 59 copied the Portuguese-keyed `auditoria.yaml`. A coordinated PR there must land before or alongside the `1.0.0` release and must also bump `quiz`'s workflow pip pin from `0.2.0` to `1.0.0` so the renamed keys are accepted by the new schema. Both repos ship in lockstep.

### D6. Fail-loud at load, fail-silent at runtime never

If a Portuguese key reaches `carregar_configuracao`, the load fails before any audit step starts. No degraded audit run is permitted.

## Risks / Trade-offs

| [Risk] | → Mitigation |
|---|---|
| New PT keys added in future versions silently pass because no enforcement against new PT. | CI drift guard asserting `set(_PT_TO_EN.values()) ⊆ _LOCALIZED_CONFIG_KEYS`. New EN keys must exist before they can be suggested. |
| `docs/MIGRATION.md` table drifts from `_PT_TO_EN` source of truth. | CI drift guard asserting `set(MIGRATION.md col1) == set(_PT_TO_EN.keys())`. |
| External consumers parse the text report by string match; new English content breaks their grep. | JSON / SARIF output schema unchanged structurally. CHANGELOG `BREAKING CHANGE` notice calls out text-value changes for scraper authors. |
| PyPI immutable — true rollback impossible if `1.0.0` ships broken. | Snapshot tests + drift guards + self-audit gate at PR time. Bump to `1.0.1` for text-only patches (no schema change ⇒ no `!` marker). |
| Docstring translation drift (left-over PT strings in `src/`). | CI docstring scan: regex over `*.py` rejects common PT tokens (`não`, `para`, `com`) outside an allowlist for variable names. |
| Cross-repo companion PR on `quiz` slips past `1.0.0` release. | Coordinate via PR description; tag `1.0.0` only after the companion merges. |
| `_PT_TO_EN` itself is wrong on first try (typo'd EN key in dict). | Snapshot test pins canonical mapping; reviewer must ratify the dict before merge. |
| Internal log strings left in source locale look like incomplete work to external readers. | Documented as deliberate per proposal non-goal in the CHANGELOG entry. |

## Migration Plan

Single `1.0.0` release. No graduated ramp. Architectural sequencing (the executable task ordering lives in `tasks.md`):

1. **Schema migration first** — land `_PT_TO_EN`, `_LOCALIZED_CONFIG_KEYS`, `_validar_chave_localizada`, and the `ConfigError` upgrade path. Load-time failure is now reachable.
2. **Surface migration** — translate consumer-facing strings, templates, README, docs, and skill in one pass. Order within the pass is implementation-defined; all surfaces ship together because the release is atomic.
3. **Documentation companion** — author `docs/MIGRATION.md` (single source of truth for the PT→EN key table).
4. **Test scaffold** — add drift-guard tests, snapshot tests, contract tests on JSON / SARIF schema stability, self-audit check.
5. **Version + release** — bump `pyproject.toml` to `1.0.0`; author `CHANGELOG.md` `BREAKING CHANGE` entry; self-audit gate must pass before tag.
6. **Cross-repo lockstep** — open and merge the companion PR on `frederico-mello/quiz` (renames keys + bumps workflow pip pin to `1.0.0`); only then publish `1.0.0` to PyPI.

**Rollback:**
- True rollback not possible (PyPI immutable).
- Text-fix hotfix: `1.0.1` within hours, no schema delta.
- Schema-revert hotfix: would itself be a breaking release; avoided via tight scope and gates.

**Consumer notification:**
- `CHANGELOG.md` `BREAKING CHANGE` entry.
- PyPI long description blurb.
- `README.md` top-of-file schema link to `docs/MIGRATION.md`.
- `docs/MIGRATION.md` linked from every doc surface.

## Open Questions

1. **`quiz` companion PR shape:** single commit (config keys + workflow bump) or split for review clarity? — Default resolution: single commit, one PR; revisit if review friction shows up.
2. ~~**`MIGRATION.md` placement**~~ — **Resolved**: `docs/MIGRATION.md`. Aligned with `docs/RELEASES.md` convention. All references in this document are updated.
3. **`configuracao_sem_integracao` rule key EN name.** — **Resolved**: `unintegrated_configurations` (aligns with `tracked_secrets` / `broken_internal_links` naming pattern; preserved semantic of "configuration without integration"). Add to canonical `_PT_TO_EN` table.
4. **Future rule additions post-`1.0.0`.** — **Resolved**: only EN-keyed rules ship; the legacy PT inventory is frozen at `1.0.0`. Documented in `docs/MIGRATION.md`.
