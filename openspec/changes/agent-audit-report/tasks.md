## 1. Default agent report and terminal summary

- [ ] 1.1 Distinguish omitted `--format` from explicit `--format text` in CLI argument handling.
- [ ] 1.2 Add default JSON report metadata with schema version, UTC timestamp, auditor version, normalized directory, and sanitized audit result.
- [ ] 1.3 Add default report persistence at `.repository-hygiene/auditoria.json`, including replacement of prior output and atomic complete writes.
- [ ] 1.4 Add concise terminal summary with status, error count, warning count, and report path for normal audits.
- [ ] 1.5 Add tests proving default clean and failed audits produce the expected summary, JSON content, sanitization, exit codes, and no truncated report after write failure.

## 2. Explicit formats and custom output

- [ ] 2.1 Preserve complete terminal output for explicit text, JSON, and SARIF formats.
- [ ] 2.2 Add `--output` handling for JSON by default and for explicitly selected formats, resolving relative paths against the audited directory.
- [ ] 2.3 Validate custom output parents and write failures, returning execution error status without presenting incomplete reports as successful.
- [ ] 2.4 Add tests covering explicit formats, custom paths, missing parents, invalid paths, overwrites, persistence failures, and exit codes `0`, `1`, and `2`.
- [ ] 2.5 Document breaking stdout behavior and migration to explicit formats or the JSON report.

## 3. Pre-commit safety and agent guidance

- [ ] 3.1 Keep pre-commit mode from creating an implicit report while allowing explicitly requested output, including default JSON when no explicit format is selected.
- [ ] 3.2 Exclude the default generated report directory from unexpected-artifact findings without excluding custom output paths.
- [ ] 3.3 Add regression tests covering pre-commit snapshot behavior, explicit `--pre-commit --output`, JSON default format, persistence failure code `2`, and later audits after default report generation.
- [ ] 3.4 Document the optional `AGENTS.md` instruction identifying `.repository-hygiene/auditoria.json` as the complete source, prioritizing errors, avoiding sensitive values, and rerunning audits after corrections.
- [ ] 3.5 Verify execution and documentation leave an existing `AGENTS.md` unchanged.
