## 1. Configuration And Modes

- [ ] 1.1 Define configuration schema for explicit `pre-commit`, `ci`, and optional automatic mode selection
- [ ] 1.2 Define default failure/report policies for confirmed, probable, ambiguous, and rejected findings
- [ ] 1.3 Update generated configuration and hook/workflow templates to select the intended mode

## 2. Repository Index And Resolution

- [ ] 2.1 Implement a per-run repository index for tracked paths, filesystem paths, directories, and ignored/runtime roots
- [ ] 2.2 Replace repeated path lookups with index-backed exact and relative resolution
- [ ] 2.3 Implement unique basename, ambiguous basename, missing, and historical resolution outcomes
- [ ] 2.4 Add tests for `app/routes.py`, `app/templates/*.html`, `scripts/*.py`, and ambiguous duplicate basenames

## 3. Reference Classification

- [ ] 3.1 Separate candidate extraction from classification and filesystem validation
- [ ] 3.2 Add format-aware handling for YAML, JSON, Markdown, Python, shell, and HTML contexts
- [ ] 3.3 Classify versions, dotted properties, URLs/schemes, runtime paths, placeholders, and templates
- [ ] 3.4 Preserve strong signals for filesystem APIs, imports, explicit path fields, links, and command arguments
- [ ] 3.5 Add regression tests covering all false-positive categories from `gerenciador-jogos`

## 4. OpenSpec Awareness

- [ ] 4.1 Detect OpenSpec repositories from supported metadata and directory markers
- [ ] 4.2 Add semantic classification for OpenSpec properties and artifact path metadata
- [ ] 4.3 Treat OpenSpec patterns and placeholders as templates rather than literal paths
- [ ] 4.4 Treat archive content as historical and prevent archive-only findings from failing CI
- [ ] 4.5 Add tests for OpenSpec and non-OpenSpec repositories

## 5. Optional LLM Triage

- [ ] 5.1 Define provider, model, enabled state, timeout, and offline configuration
- [ ] 5.2 Implement a closed classification request for ambiguous pre-commit occurrences
- [ ] 5.3 Redact recognized secrets and minimize context before provider requests
- [ ] 5.4 Validate and deterministically verify LLM-suggested candidate paths
- [ ] 5.5 Handle provider failure or invalid output as ambiguity without creating a false failure
- [ ] 5.6 Add tests using a fake provider, disabled provider, redaction, and provider failure

## 6. Reporting And Exit Status

- [ ] 6.1 Add additive classification, confidence, candidate, reason, and policy-action fields to result objects
- [ ] 6.2 Update text, JSON, and SARIF reporters for ambiguous and historical findings
- [ ] 6.3 Implement mode-specific exit status behavior with confirmed-only CI failure by default
- [ ] 6.4 Document provider disclosure, privacy behavior, and no-LLM operation

## 7. Validation And Rollout

- [ ] 7.1 Build a fixture corpus for versions, properties, runtime paths, templates, archives, and real application paths
- [ ] 7.2 Measure precision and recall separately for pre-commit and CI modes
- [ ] 7.3 Run the audit against `gerenciador-jogos` and verify that known existing files are not reported missing
- [ ] 7.4 Preserve a compatibility path for legacy configuration during migration
- [ ] 7.5 Update README and release notes with mode selection and migration guidance
