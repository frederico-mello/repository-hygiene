## Context

The `validar_commits` function in `commit_check.py` iterates over all non-merge commits from `git log --no-merges` and validates each subject against the Conventional Commits regex. Merge commits are already filtered by `--no-merges`, but `git revert` commits pass through. Their auto-generated subject (`Revert "<original>"`) does not match the Conventional Commits pattern, producing false positives.

The change adds a pre-check before the regex: if the subject starts with `Revert "`, skip validation for that commit.

## Goals / Non-Goals

**Goals:**
- Exclude git revert commits from conventional-commits validation
- Detect via subject prefix `Revert "` (git's standard auto-message format)
- Zero performance impact on the existing audit path

**Non-Goals:**
- Detecting revert commits via commit body inspection
- Exempting manually-written revert-style messages (e.g., `revert: fix X`)
- Adding configurable exemption patterns to `auditoria.yaml`
- Changing the Conventional Commits regex or accepted types

## Decisions

### Decision 1: Subject-line prefix check over body inspection

**Choice:** Check if commit subject starts with `Revert "` before running the Conventional Commits regex.

**Rationale:** `git revert` always generates the format `Revert "<original subject>"` for the first line. Checking the body for `This reverts commit <hash>` would require either reading the full commit message (extra `git log` format field) or an additional `git show` per commit — both add complexity and runtime cost with no practical gain. The subject prefix is a reliable, zero-cost signal already available from the existing `git log --format=%H%x00%s` output.

## Risks / Trade-offs

- [False negative — custom revert message] A commit with subject `Revert fix bug` (no quotes, no Conventional Commits prefix) would be skipped but is not a git-generated revert. Mitigation: this format is not produced by `git revert`; manual reverts should use `revert:` per Conventional Commits. Unlikely in practice.
- [False positive — coincidental prefix] A commit whose subject legitimately starts with `Revert "` but is not a git revert would be skipped. Mitigation: `Revert "` is not a valid Conventional Commits type, so such a message would already be flagged. Skipping it is harmless.
