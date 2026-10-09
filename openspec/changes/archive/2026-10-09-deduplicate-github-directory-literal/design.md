# Design

## Context

See proposal.md for motivation. `core.py` already groups directory-name constants near the top of the module; the three target literals refer to the same `.github` directory value. The longer `.github` path strings are distinct values and remain out of scope.

## Goals / Non-Goals

**Goals:** Reuse the existing module-level constant pattern and preserve the three call sites' current values and behavior.

**Non-Goals:** Change path matching, audit results, CLI/report contracts, or any longer GitHub-related path literal.

## Decisions

- Add `_DIR_GITHUB = ".github"` beside the existing `_DIR_*` definitions and substitute it only at the three duplicate-literal sites. This follows the module's existing convention and avoids introducing another helper or abstraction. Keeping the literals inline would retain the Sonar finding; replacing broader strings would expand scope and alter distinct values.
- Declare no spec delta: the change affects source organization only, so `.openspec.yaml` uses `skip_specs: true` rather than inventing a behavior requirement.

## Risks / Trade-offs

- [Risk] A broader replacement could alter the distinct strings `".github/prompts/"`, `".github/skills/openspec-"`, or `".github/"` → [Mitigation] Keep the substitutions limited to the three exact duplicate literals and explicitly verify those longer strings remain unchanged.
- [Risk] A typo in the constant or one replacement could change path handling → [Mitigation] Run the specified test suite and compare its result against the recorded baseline.

## Migration Plan

No data migration, deployment coordination, or compatibility shim is required. Apply the constant extraction as one source change; rollback by reverting the constant and its three uses together.
