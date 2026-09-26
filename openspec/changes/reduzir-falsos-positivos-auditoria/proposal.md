## Why

The audit currently interprets versions, structured properties, runtime paths, templates, and historical OpenSpec content as live filesystem references. This produces a very high false-positive rate and makes the audit unsuitable for reliable CI enforcement.

The tool needs separate policies for broad developer feedback and conservative CI validation, while preserving optional LLM assistance without requiring repository content to leave the user's chosen environment.

## What Changes

- Add explicit `pre-commit` and `ci` audit modes with different confidence and failure policies.
- Introduce structured reference classification instead of treating every dotted string as a filesystem path.
- Build a repository path index and resolve exact, relative, basename, ambiguous, runtime, template, and historical references explicitly.
- Make OpenSpec support optional and activate semantic rules only when OpenSpec is detected.
- Treat archive content as historical context rather than current filesystem state.
- Add optional, user-configured LLM classification for ambiguous pre-commit findings.
- Add `confirmed`, `probable`, `ambiguous`, and rejected outcomes to reports and policies.
- Add privacy controls for LLM use, including provider disclosure, secret redaction, context minimization, and an offline option.
- Ensure conservative CI mode reports or fails only on deterministic, high-confidence missing references.

## Capabilities

### New Capabilities
- `reference-classification`: Classify and resolve candidate references with confidence and provenance.
- `audit-execution-modes`: Apply distinct pre-commit and CI policies to findings.
- `optional-llm-triage`: Use a configured LLM only for ambiguous candidate classification.
- `openspec-awareness`: Detect OpenSpec and apply semantic rules for its artifacts, properties, templates, and archives.

### Modified Capabilities
- None. No existing OpenSpec specification files were found in the repository.

## Impact

- Affects the core audit pipeline, reference and documentation rules, reporting output, configuration schema, and pre-commit/CI integration.
- Adds no mandatory external runtime dependency; LLM integration is optional and provider-configured.
- Existing reports may gain classification, confidence, candidates, and reason fields.
- Existing consumers that assume every finding is binary may need to handle additional statuses.
