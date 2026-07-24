---
name: agent-hygiene-flow
description: >
  Orchestrates the complete repository hygiene remediation loop: verify target
  and configuration, run audit, consume the canonical JSON report, triage findings
  by severity, remediate per rule, re-audit after corrections, converge to clean
  or blocked, and clean up temporary artifacts. Activates on hygiene, audit, and
  repository cleanup requests.
---

# Agent Hygiene Flow

## Purpose

You are executing the repository hygiene remediation flow. Follow every step in
order. Do not skip, shortcut, or improvise alternative sequences. The goal is a
clean audit — no error findings, no unhandled residual findings.

## Phase 1: Target and Configuration

1. Verify the audit target is a valid Git repository. If not, stop and report
   that the target is invalid. Do not run any audit.
2. Check whether `auditoria.yaml` exists in the repository root:
   - If it exists: preserve and use it. Never overwrite or modify it.
   - If it does not exist: you MAY initialize it through the supported CLI flow
     (`repository-hygiene --init .`). Do not silently overwrite any configuration
     that appears during initialization.
3. Do not modify `AGENTS.md`, `.gitignore`, or any unrelated file during this
   phase.

## Phase 2: Audit Execution

1. Run the audit in normal mode:
   ```
   repository-hygiene .
   ```
2. Interpret the exit code as an initial signal only:
   - `0`: clean audit. Still proceed to read the canonical report — the exit
     code is never a substitute for the report.
   - `1`: findings exist. Proceed to read the canonical report.
   - `2`: configuration or execution error. Stop and report the error. Do not
     attempt to remediate findings until the error is resolved.

## Phase 3: Canonical Report Consumption

1. Read `.repository-hygiene/auditoria.json` as the canonical, sanitized source
   of findings.
2. If the report is missing, invalid, or cannot be parsed as valid sanitized
   JSON: stop the flow and report that no reliable source is available. Do not
   infer findings from partial terminal output or any other source.
3. Never reproduce, search for, or attempt to reconstruct a masked sensitive
   value from the report in responses, logs, or edits. All report content is
   sanitized; use only the masked representation.

## Phase 4: Triage

1. Order all findings: every `error` finding before any `warning` finding.
2. Group findings by their originating rule.
3. Consult the triage matrix below for each finding. The matrix maps every audit
   rule to its expected remediation action and whether the severity blocks
   (`error`) or only informs (`warning`). The severities MUST match those emitted
   by the auditor — do not redefine them.

### Triage Matrix

| Rule | Default Severity | Remediation Action |
|---|---|---|
| `segredos_rastreados` | error (blocks) | Remove or replace the detected secret. Add the file to `.gitignore` or to `auditoria.yaml` exceptions if the match is a false positive. |
| `links_internos_quebrados` | error (blocks) | Fix the broken link target or remove the link. |
| `referencias_inexistentes` | error (blocks) | Remove the dangling reference or create the referenced file. |
| `artefatos_fora_gitignore` | error (blocks) | Add the artifact pattern to `.gitignore` or remove the generated file. |
| `gitkeep_sem_conteudo` | warning (informs) | Remove directories containing only `.gitkeep` that serve no purpose, or add meaningful content. |
| `arquivos_sem_referencia` | warning (informs) | Add references to the unreferenced file in documentation or code, or consider removal. |
| `documentacao_desatualizada` | warning (informs) | Update documentation to remove or correct references to files that no longer exist. |
| `configuracao_sem_integracao` | warning (informs) | Add a CI workflow, pre-commit hook, or usage documentation so the configuration is operational. |
| `openspec_parada` | warning (informs) | Archive stalled OpenSpec changes older than 30 days, or continue them. |
| `workflows_inseguros` | warning (informs) | Restrict workflow permissions to the minimum required, and pin third-party action versions. |

## Phase 5: Remediation

1. Process findings in order: all `error` findings before any `warning` finding,
   grouped by rule.
2. For each finding, apply the remediation action from the triage matrix. Fix
   only what the finding specifies — do not refactor adjacent code or fix
   unrelated problems.
3. **Worktree isolation (MANDATORY):** any code or repository edit motivated by
   a finding MUST occur in an isolated worktree created via `git-wt switch -c`
   (Worktrunk; see AGENTS.md for prerequisites) and MUST be delivered through
   push and pull request. Never edit files directly on the protected branch
   (main/master).
4. Do not modify `AGENTS.md`, `.gitignore`, configuration files, or any file
   not referenced by a finding unless a matching finding and operational
   authorization exist. This prohibition does not apply to `auditoria.yaml`
   initialization performed during Phase 1, which is not a remediation action.

## Phase 6: Re-Audit

1. After completing a coherent batch of corrections, re-run the audit:
   ```
   repository-hygiene .
   ```
2. The new report replaces the previous one. Read it as the canonical source
   before further triage.
3. Repeat from Phase 4 until one of the termination conditions in Phase 7 is met.

## Phase 7: Termination

1. **Clean termination:** if an audit returns exit code `0` and no remaining
   actionable findings exist, proceed to Phase 8 (Cleanup).
2. **Blocked — no progress:** if a remediation produces no progress (the same
   finding persists unchanged) and no safe alternative remediation is available,
   stop repeating corrections and report the flow as blocked with the residual
   finding.
3. **Residual acceptance:** a residual finding of any severity MAY be classified
   as non-actionable only through an explicit user decision. Such acceptance
   MUST be accompanied by a recorded justification in the execution result.
   Without explicit user acceptance, the flow terminates as blocked — never as
   clean.

## Phase 8: Cleanup

Execute these steps ONLY after a clean audit and the completion of all
corrections. If the flow terminated as blocked, do NOT perform cleanup.

1. Remove `.repository-hygiene/auditoria.json`.
2. Remove the `.repository-hygiene/` directory.
3. Before removal, validate all of the following:
   - The path is under the audited repository root.
   - The path does not follow an external link or symlink outside the root.
   - The directory contains only the expected report file (`auditoria.json`).
   If any check fails, REFUSE removal and leave all files in place.
4. Do not use broad or forced removal (no `rm -rf`, no recursive delete without
   validation). Only the two exact paths above may be removed.
5. If removal fails for any reason: report the cleanup failure explicitly. Never
   present cleanup as completed when it was not.

## Security Rules

- **Sensitive values:** all audit report content is sanitized. Never reproduce,
  search for, or attempt to reconstruct masked values. Use only the masked
  representation provided by the report.
- **Worktree isolation:** every code edit motivated by a finding goes through
  `git-wt switch -c` → commit → push → `gh pr create`. No direct edits to
  main/master. (`git-wt` is Worktrunk, the project's mandatory worktree
  isolation tool. See AGENTS.md for prerequisites.)
- **Temporary artifacts:** `.repository-hygiene/auditoria.json` and
  `.repository-hygiene/` are temporary. Remove them after a clean flow. Do not
  commit, version, archive, or share them.
