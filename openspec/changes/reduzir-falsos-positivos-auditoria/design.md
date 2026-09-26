## Context

The current implementation scans quoted strings with broad regular expressions and immediately checks them as filesystem paths. This conflates file references with versions, dotted properties, runtime values, URL-like schemes, placeholders, and historical documentation. Path existence is also checked repeatedly without a shared repository index.

The tool is used both as a pre-commit aid and as a CI gate. These contexts have different tolerances: pre-commit can investigate broadly, while CI must avoid false-positive failures. OpenSpec may or may not be present in the audited repository.

## Goals / Non-Goals

**Goals:**

- Make CI reference checks deterministic and conservative.
- Preserve broader pre-commit discovery through confidence levels and optional LLM triage.
- Distinguish current, runtime, template, property, URL, and historical references.
- Resolve references against one indexed view of Git-tracked and filesystem paths.
- Provide semantic OpenSpec behavior only when OpenSpec is detected.
- Make LLM data flow explicit, minimized, and configurable.

**Non-Goals:**

- Guarantee semantic understanding of arbitrary prose.
- Require an LLM or a remote service.
- Treat every runtime-generated file as a repository artifact.
- Make archived documents pass current-state validation.
- Rewrite all existing audit rules unrelated to reference detection.

## Decisions

### Separate policy modes

The command SHALL support explicit `pre-commit` and `ci` modes. Pre-commit SHALL report broad findings and may invoke configured LLM triage. CI SHALL default to deterministic classification, ignore ambiguous findings for exit status, and fail only on confirmed missing references.

An automatic mode may infer a default, but explicit mode selection remains authoritative.

### Structured classification before existence checking

Candidate extraction, classification, path resolution, and policy decision SHALL be separate stages. A string SHALL not be checked as a filesystem path until it has been classified as a possible file reference.

Format-aware parsing and contextual signals SHALL supplement regex extraction. Strong signals include filesystem APIs, explicit path fields, Markdown links, imports, and command arguments. Version strings, dotted properties, schemes, placeholders, and known runtime paths SHALL be rejected or downgraded.

### Shared repository index and resolution confidence

The auditor SHALL construct a repository index once per run, containing tracked paths, existing paths, directories, and relevant aliases. Resolution SHALL distinguish exact, relative, unique basename, ambiguous, and missing matches. A basename match SHALL not silently become an exact match when multiple files share that name.

### OpenSpec detection and semantics

OpenSpec behavior SHALL be enabled only when the repository contains recognizable OpenSpec metadata or structure. Known OpenSpec properties and artifact patterns SHALL be classified as logical metadata or templates, not live files. Archive directories SHALL be historical by default: pre-commit may report informational findings, but CI SHALL not fail because of them.

### Optional LLM as ambiguity resolver

The LLM SHALL be a second-stage classifier, not the source of filesystem truth. It may classify an occurrence, identify template/runtime/property intent, and suggest candidate paths. Deterministic resolution SHALL verify any suggested path.

The provider, model, enabled state, and data-sharing behavior SHALL be visible in configuration and reports. The integration SHALL support local or user-selected OpenAI-compatible providers and an explicit no-LLM mode.

### Privacy minimization

When LLM use is enabled, the system SHALL redact recognized secrets, send only the relevant context by default, limit payload size, and disclose the configured provider. CI SHALL be able to disable LLM use independently of pre-commit.

### Backward-compatible report evolution

Existing core fields SHALL remain available. New classification fields SHALL be additive where practical, including kind, confidence, resolution candidates, reason, and policy action. Text, JSON, and SARIF reporters SHALL represent ambiguous findings without treating them as errors by default.

## Risks / Trade-offs

- [Risk] Conservative CI misses a real broken reference → Mitigation: expose probable/ambiguous findings as warnings or artifacts and keep pre-commit broader.
- [Risk] LLM classifications are inconsistent → Mitigation: use closed classification values, deterministic verification, and never let LLM output alone fail CI.
- [Risk] Repository-specific semantics are not captured → Mitigation: provide configuration overrides and OpenSpec-specific rules only when detected.
- [Risk] Basename resolution remains ambiguous → Mitigation: report candidates and require unique matches for confirmed resolution.
- [Risk] Provider receives sensitive context → Mitigation: local-provider support, redaction, minimized context, explicit disclosure, and opt-out.
- [Risk] Existing consumers reject new report fields or statuses → Mitigation: additive fields and documented exit-status compatibility.

## Migration Plan

1. Preserve the current command behavior behind an explicit legacy-compatible default while introducing mode configuration.
2. Add classification fields and conservative CI policy without removing existing result fields.
3. Update generated configuration and pre-commit templates to select a mode explicitly.
4. Validate against representative repositories, including `gerenciador-jogos`, OpenSpec projects, runtime paths, and archived changes.
5. Make conservative CI the recommended configuration after false-positive metrics meet the acceptance threshold.

Rollback consists of disabling the new mode or LLM settings and using the prior rule configuration; no data migration is required.

## Open Questions

- Should `probable` findings be warnings in CI output or be omitted from the default report?
- Which OpenSpec markers are sufficient for automatic detection?
- Which runtime path prefixes and extensions belong in the default policy versus configuration?
- Should the legacy behavior remain available as a named mode or only as a temporary migration option?
