## Why

`auditoria-higiene` ships in two languages simultaneously: the package itself (PyPI name, description, CLI behavior, workflow YAML names) is English, while `auditoria.yaml` keys, README, error messages, CLI output, and code docstrings are Portuguese. The mix confuses external consumers — the recent `frederico-mello/quiz` PR #59 imported our Portuguese-keyed config and was flagged by automated review for inconsistent locale — and forces every consumer-facing surface to negotiate two conventions. We need a single canonical locale so the project behaves as one product for users, contributors, and audit bots.

**Scope boundary (critical):** this change governs the locale of content *shipped from this repository* — our own config schema, CLI strings, templates, docs, and skill — and the load-time failure when an external `auditoria.yaml` still carries Portuguese keys. It does **not** add an audit rule that detects locale mix inside the repositories the tool is run against. That capability is a separate change.

## What Changes

- **BREAKING (contract — load-time failure)**: loading an `auditoria.yaml` that uses Portuguese keys now raises a load-time error naming the offending keys and pointing to the migration guide. English keys become the only accepted schema.
- **BREAKING (config schema)**: top-level keys (`versao_configuracao`, `regras`, `excecoes`), rule identifiers (`segredos_rastreados`, `links_internos_quebrados`, `workflows_inseguros`, etc.), and configuration subkeys (`habilitada`, `severidade`, `permissoes_write_permitidas`) are renamed to English.
- **BREAKING (default config)**: the `auditoria.yaml` shipped by `install` is rewritten in English with the new key names.
- **BREAKING (CLI text)**: CLI error messages, report text, and `repository-hygiene --help` output switch to English. Structured output (JSON, SARIF) keeps the same schema; only labels/messages change.
- **BREAKING (docs and skill)**: `README.md`, `docs/`, the `agent-hygiene-flow` skill, and code docstrings rewrite to English. The Portuguese-only stance of PR `d5a1963` is reverted deliberately.

### Not in scope

- No i18n framework, locale negotiation, or translatable message catalog is introduced. English is the only locale.
- No automated translation tooling; each surface is rewritten by hand.
- No backports or compatibility shims for legacy Portuguese keys; the load-time failure is the migration signal.
- Out-of-tree reformatting (JSON/SARIF output labels, internal log strings, error stack traces, dependency lockfiles) is left to follow-up changes.

## Capabilities

### New Capabilities
- `english-source-locale`: Establishes English as the canonical locale for the source content shipped from this repository (config keys, CLI output, default config, README, docs, skill content, code docstrings) and makes configuration that violates the locale fail loudly at load time. The capability describes locale of the auditor's own output — it does not audit locale mix in external repositories.

### Modified Capabilities
- `documentation-consistency`: Strengthens the rule's documentation guidance to enforce English as the only locale for project-facing text in this repository (config keys, README, error messages, default config samples).

## Impact

- **Config schema (breaking)**: every consumer with a custom `auditoria.yaml` must migrate before loading the new version. Public consumers are notified via the changelog and a migration guide that ships with this change.
- **CLI surface (breaking, text only)**: any consumer parsing CLI output text or report messages must update parsers. JSON/SARIF output is unchanged structurally.
- **Docs surface**: `README.md` rewrite deliberately supersedes the Portuguese-only stance taken in PR `d5a1963`.
- **Skill content**: `agent-hygiene-flow` skill text switches to English; downstream OpenCode skill users pick up the change on next install.
- **SemVer signaling**: this release is marked `1.0.0` per SemVer to communicate the breaking contract change to consumers.
- **Cross-repo consumer (`frederico-mello/quiz`)**: the config copied into `quiz` PR #59 is Portuguese-keyed; a coordinated update in that repo lands before or alongside this release so `quiz` is not broken at runtime.
