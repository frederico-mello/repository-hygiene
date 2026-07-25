## 1. Skill and command are discoverable and delegate to one source

- [x] 1.1 Create the agent-hygiene-flow skill under `.opencode/skills/` with front matter and a description that enables automatic activation on hygiene, audit, or repository-cleanup requests.
- [x] 1.2 Create the `/hygiene` command under `.opencode/commands/` as an operational entry point that routes the agent to the agent-hygiene-flow skill and accepts an optional repository target or hygiene objective.
- [x] 1.3 Ensure the command contains no normative flow logic, triage matrix, remediation actions, or termination conditions, so the skill remains the single source that defines the flow.
- [x] 1.4 Verify the skill and command structure, front matter, and activation behavior against the OpenCode conventions and confirm `/hygiene` resolves to the skill.

## 2. Agent verifies the target and reads the canonical report before triaging

- [x] 2.1 Instruct the agent to verify the audit target is a valid repository and to stop with an invalid-target report before running any audit.
- [x] 2.2 Instruct the agent to preserve and use an existing `auditoria.yaml` without overwriting it, and to initialize a missing configuration only through the flow supported by the CLI.
- [x] 2.3 Instruct the agent to execute the `repository-hygiene` CLI in normal mode and to treat exit codes `0`, `1`, and `2` as an initial signal only, never as a substitute for the report.
- [x] 2.4 Instruct the agent to read `.repository-hygiene/auditoria.json` as the canonical sanitized source of findings after each audit and to never infer findings from partial terminal output.
- [x] 2.5 Instruct the agent to stop the flow and report that no reliable source is available when the report is missing, invalid, or otherwise untrustworthy.

## 3. Agent triages findings by severity and remediates them safely

- [x] 3.1 Document, inside the skill, a triage matrix mapping each audit rule (`segredos_rastreados`, `links_internos_quebrados`, `referencias_inexistentes`, `artefatos_fora_gitignore`, `gitkeep_sem_conteudo`, `arquivos_sem_referencia`, `documentacao_desatualizada`, `configuracao_sem_integracao`, `openspec_parada`, `workflows_inseguros`) to its expected remediation action and blocking-versus-informing severity, matching the severities emitted by the auditor without redefining them.
- [x] 3.2 Instruct the agent to order findings so every `error` finding is addressed before any `warning` finding and to group findings by their originating rule.
- [x] 3.3 Codify the project rule that any code or repository edit motivated by a finding occurs in an isolated worktree and is delivered through push and pull request, with no direct edits to the protected branch.
- [x] 3.4 Instruct the agent to treat all report content as sanitized and to never reproduce, search for, or reconstruct a masked sensitive value in responses, logs, or edits.
- [x] 3.5 Instruct the agent not to modify `AGENTS.md`, `.gitignore`, configuration files, or unrelated files during remediation unless a matching finding and operational authorization exist, with an explicit carve-out for `auditoria.yaml` initialization performed under the verification step.

## 4. Agent re-audits and converges to a clean state or an explicit block

- [x] 4.1 Instruct the agent to re-run the audit after each coherent batch of corrections and to let the new report replace the previous one before further triage.
- [x] 4.2 Instruct the agent to terminate the flow as clean only when an audit returns exit code `0` and no remaining actionable findings exist.
- [x] 4.3 Instruct the agent to stop repeating corrections and report the flow as blocked when a remediation produces no progress and no safe alternative remains.
- [x] 4.4 Instruct the agent that a residual finding of any severity may be classified as non-actionable only through an explicit user decision with a recorded justification, and that without such acceptance the flow terminates as blocked.

## 5. Temporary artifact cleanup after a clean flow

- [x] 5.1 Instruct the agent to remove `.repository-hygiene/auditoria.json` and the `.repository-hygiene/` directory only after a clean audit and the completion of corrections.
- [x] 5.2 Instruct the agent to validate, before removal, that the path is under the audited repository root, does not follow an external link, and contains only the expected report, refusing removal otherwise.
- [x] 5.3 Instruct the agent to refuse broad or forced removal and to leave all files in place when validation fails or the directory holds unexpected content.
- [x] 5.4 Instruct the agent to report any cleanup failure explicitly and never present cleanup as completed when it was not.
