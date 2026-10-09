# Proposal

## Why

SonarCloud rule `python:S1192` flags the literal `".github"` duplicated three times in `src/auditoria_higiene/core.py` (issue #709). Defining one module-level constant will remove the duplication and reduce maintenance risk without changing path handling or audit behavior.

## What Changes

- Define `_DIR_GITHUB = ".github"` beside the existing `_DIR_*` constants and replace only the three matching occurrences.
- Leave the longer strings `".github/prompts/"`, `".github/skills/openspec-"`, and `".github/"` unchanged.
- No public API, dependency, or user-visible behavior changes.

## Capabilities

### New Capabilities

None. This change introduces no new system behavior.

### Modified Capabilities

None. This is an internal refactor with no requirement-level behavior change; the change metadata opts out of specs.

## Impact

The only affected source file is `src/auditoria_higiene/core.py`. The expected effect is limited to removing the duplicate literal while preserving existing results and path semantics.
