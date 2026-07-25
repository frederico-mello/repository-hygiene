## ADDED Requirements

### Requirement: Skill is the normative source for the hygiene flow

The project SHALL provide a single OpenCode skill that normatively defines the agent hygiene remediation flow, including activation context, audit execution, report consumption, finding triage, remediation, re-audit, termination conditions, and temporary artifact cleanup. Any other document that references the flow SHALL defer to this skill rather than redefining it.

#### Scenario: Skill present and discoverable
- **GIVEN** the repository contains the agent-hygiene-flow skill under `.opencode/skills/`
- **WHEN** an agent looks up how to manage repository hygiene
- **THEN** the skill SHALL be the authoritative source for the flow
- **AND** no second conflicting definition of the flow SHALL exist in the repository

### Requirement: Explicit /hygiene entry command delegates to the skill

The project SHALL provide an explicit `/hygiene` command that acts as an operational entry point and SHALL only direct the agent to the agent-hygiene-flow skill. The command SHALL NOT duplicate the triage matrix, remediation actions, or termination conditions.

#### Scenario: Command invokes the skill
- **GIVEN** the `/hygiene` command is available
- **WHEN** an agent receives the `/hygiene` invocation
- **THEN** the command SHALL route the agent to the agent-hygiene-flow skill
- **AND** the command SHALL NOT contain normative flow logic

#### Scenario: Command accepts an optional target
- **GIVEN** the `/hygiene` command accepts an optional repository target or hygiene objective
- **WHEN** a target is supplied
- **THEN** the agent SHALL apply the skill flow to that target
- **BUT** absence of a target SHALL NOT prevent the flow from running against the current repository

### Requirement: Skill auto-activates on hygiene-related requests

The skill description SHALL enable automatic activation when an agent receives a request related to repository hygiene, audit, or cleanup, even when `/hygiene` is not explicitly invoked.

#### Scenario: Natural-language hygiene request loads the skill
- **GIVEN** an agent receives a request mentioning hygiene, audit, or repository cleanup
- **WHEN** no explicit `/hygiene` is supplied
- **THEN** the agent-hygiene-flow skill SHALL be eligible for automatic activation
- **AND** the flow behavior SHALL remain identical to the explicit command path

### Requirement: Target and configuration are verified before auditing

The agent SHALL verify that the audit target is a valid repository and SHALL check for an existing `auditoria.yaml`. When no configuration exists, the agent MAY initialize it through the flow supported by the CLI; when a configuration already exists, the agent SHALL preserve and use it without overwriting it.

#### Scenario: Existing configuration is preserved
- **GIVEN** the target repository already contains an `auditoria.yaml`
- **WHEN** the agent begins the hygiene flow
- **THEN** the agent SHALL use the existing configuration
- **AND** the agent SHALL NOT overwrite or replace the existing `auditoria.yaml`

#### Scenario: Missing configuration may be initialized
- **GIVEN** the target repository has no `auditoria.yaml`
- **WHEN** the agent begins the hygiene flow
- **THEN** the agent MAY initialize the configuration through the supported CLI flow
- **AND** the agent SHALL NOT silently overwrite an existing configuration that appears during initialization

#### Scenario: Target is not a valid repository
- **GIVEN** the supplied target is not a valid repository
- **WHEN** the agent begins the hygiene flow
- **THEN** the agent SHALL stop the flow
- **AND** the agent SHALL report that the target is invalid before running any audit

### Requirement: Audit execution interprets the CLI exit code as an initial signal

The agent SHALL execute the `repository-hygiene` CLI in normal mode and SHALL treat its exit code as an initial signal only: `0` indicates a clean audit, `1` indicates that findings exist, and `2` indicates a configuration or execution error. The exit code SHALL NOT be used as a substitute for reading the audit report, including in the clean case.

#### Scenario: Exit code signals a clean audit
- **GIVEN** the CLI exits with code `0`
- **WHEN** the agent interprets the result
- **THEN** the agent SHALL treat the exit as indicating a clean audit
- **AND** the agent SHALL still read the canonical report before declaring the flow clean

#### Scenario: Exit code signals findings
- **GIVEN** the CLI exits with code `1`
- **WHEN** the agent interprets the result
- **THEN** the agent SHALL treat the exit as indicating findings
- **AND** the agent SHALL proceed to read the canonical report

#### Scenario: Exit code signals execution error
- **GIVEN** the CLI exits with code `2`
- **WHEN** the agent interprets the result
- **THEN** the agent SHALL treat the exit as a configuration or execution error
- **AND** the agent SHALL NOT attempt to remediate findings until the error is resolved

### Requirement: Canonical report is consumed from the JSON artifact

The agent SHALL read `.repository-hygiene/auditoria.json` as the canonical, sanitized source of findings after each audit. The agent SHALL NOT infer findings from partial terminal output or from any source other than that report.

#### Scenario: Report read after audit
- **GIVEN** an audit has completed and produced `.repository-hygiene/auditoria.json`
- **WHEN** the agent needs the current findings
- **THEN** the agent SHALL read the report file
- **AND** the agent SHALL treat the report as the single source of truth for findings

#### Scenario: Partial output is not trusted
- **GIVEN** terminal output contains fragmentary findings
- **WHEN** the report file is absent or incomplete
- **THEN** the agent SHALL NOT use the fragmentary output as a finding source

### Requirement: Unreliable report halts the flow

When the report is missing, invalid, or otherwise untrustworthy, the agent SHALL stop the flow and report that no reliable source is available for a decision.

#### Scenario: Missing report
- **GIVEN** the audit did not produce `.repository-hygiene/auditoria.json`
- **WHEN** the agent attempts to read the report
- **THEN** the agent SHALL stop the flow
- **AND** the agent SHALL report that no reliable audit source is available

#### Scenario: Invalid report
- **GIVEN** the report exists but cannot be parsed as valid sanitized JSON
- **WHEN** the agent attempts to read the report
- **THEN** the agent SHALL stop the flow
- **AND** the agent SHALL NOT proceed to triage or remediation

### Requirement: Findings are prioritized by severity and grouped by rule

The agent SHALL order findings so that every `error` finding is addressed before any `warning` finding, and SHALL group findings by their originating rule to drive coherent remediation.

#### Scenario: Errors take precedence over warnings
- **GIVEN** the report contains findings of severity `error` and `warning`
- **WHEN** the agent orders the work
- **THEN** every `error` finding SHALL be considered before any `warning` finding
- **AND** findings SHALL be grouped by their rule

#### Scenario: Warnings addressed after errors
- **GIVEN** all `error` findings have been remediated and `warning` findings remain
- **WHEN** the agent continues the flow
- **THEN** the agent SHALL proceed to the remaining `warning` findings

### Requirement: Each rule maps to a remediation action and blocking severity

The skill SHALL document a triage mapping from each audit rule (`segredos_rastreados`, `links_internos_quebrados`, `referencias_inexistentes`, `artefatos_fora_gitignore`, `gitkeep_sem_conteudo`, `arquivos_sem_referencia`, `documentacao_desatualizada`, `configuracao_sem_integracao`, `openspec_parada`, `workflows_inseguros`) to the expected remediation action and to whether that severity blocks (`error`) or only informs (`warning`). The severities recorded in the matrix SHALL match the severities emitted by the auditor and SHALL NOT be redefined by the skill.

#### Scenario: Rule maps to a remediation action
- **GIVEN** the skill documents the triage matrix
- **WHEN** the agent encounters a finding for any documented rule
- **THEN** the matrix SHALL provide an expected remediation action for that rule
- **AND** the matrix SHALL state whether the rule's severity blocks or informs
- **BUT** the matrix SHALL NOT redefine a severity different from the one emitted by the auditor

### Requirement: Code edits triggered by findings use worktree isolation

Any code or repository edit motivated by a finding SHALL be performed in an isolated worktree with push and pull request, in accordance with the project's global rules. The skill SHALL codify this requirement rather than introduce it.

#### Scenario: Remediation edit is isolated
- **GIVEN** a finding requires a code or repository edit
- **WHEN** the agent performs the edit
- **THEN** the edit SHALL occur in an isolated worktree
- **AND** the change SHALL be delivered through push and pull request

#### Scenario: No direct edits to the working branch
- **GIVEN** the global rules forbid direct edits to the main working branch
- **WHEN** the agent remediates a finding
- **THEN** the agent SHALL NOT edit files directly on the protected branch

### Requirement: Sensitive values are never reproduced

The agent SHALL treat all report content as sanitized and SHALL NEVER reproduce, search for, or attempt to reconstruct a masked sensitive value in responses, logs, or edits.

#### Scenario: Masked value stays masked
- **GIVEN** a finding contains a value masked by the auditor sanitization policy
- **WHEN** the agent reports or remediates the finding
- **THEN** the agent SHALL use only the masked representation
- **AND** the agent SHALL NOT attempt to discover or print the original value

### Requirement: Re-audit runs after each coherent correction batch

The agent SHALL re-run the audit after completing a coherent batch of corrections, and each new report SHALL replace the previous one before further triage.

#### Scenario: Re-audit after corrections
- **GIVEN** the agent has completed corrections for a set of findings
- **WHEN** the agent proceeds with the flow
- **THEN** the agent SHALL re-run the audit before acting on the next set of findings
- **AND** the new report SHALL replace any prior report

### Requirement: Loop terminates on a clean audit

The flow SHALL terminate as clean when an audit returns exit code `0` with no remaining actionable findings.

#### Scenario: Clean audit ends the flow
- **GIVEN** an audit returns exit code `0`
- **WHEN** the agent evaluates termination
- **THEN** the flow SHALL terminate as clean
- **AND** the agent SHALL proceed to temporary artifact cleanup

### Requirement: Persistent findings with no progress terminate as blocked

When a remediation produces no progress and no safe alternative remains, the agent SHALL stop repeating corrections and SHALL report the flow as blocked with the residual state, unless a residual finding is accepted as non-actionable.

#### Scenario: No-progress finding blocks the flow
- **GIVEN** a finding persists after a remediation attempt without change
- **WHEN** no safe alternative remediation is available
- **THEN** the agent SHALL stop repeating corrections
- **AND** the agent SHALL report the flow as blocked with the residual finding

### Requirement: Residual findings may be accepted only with explicit justification

A residual finding (a finding that remains after remediation has been attempted and cannot be further remediated) of any severity MAY be classified as non-actionable only through an explicit user decision, and that decision SHALL be accompanied by a recorded justification in the execution result. Without such acceptance, the flow SHALL terminate as blocked rather than as clean.

#### Scenario: Accepted residual finding recorded with justification
- **GIVEN** a residual finding remains and cannot be remediated
- **WHEN** the user explicitly accepts the finding as non-actionable
- **THEN** the agent SHALL record a justification for the acceptance
- **AND** the flow SHALL reflect the accepted residual in its result

#### Scenario: Unaccepted residual finding blocks the flow
- **GIVEN** a residual finding remains and the user has not accepted it
- **WHEN** the agent reaches termination
- **THEN** the flow SHALL terminate as blocked
- **AND** the agent SHALL NOT present the residual finding as resolved

### Requirement: Temporary artifacts are removed after a clean flow

After a clean audit and the completion of corrections, the agent SHALL remove `.repository-hygiene/auditoria.json` and the `.repository-hygiene/` directory. Removal SHALL occur only after validation, and SHALL be limited to exactly those two paths.

#### Scenario: Clean flow removes the temporary directory
- **GIVEN** the audit is clean and corrections are complete
- **WHEN** the agent performs cleanup
- **THEN** the agent SHALL remove `.repository-hygiene/auditoria.json`
- **AND** the agent SHALL remove the `.repository-hygiene/` directory

#### Scenario: Unexpected directory content blocks removal
- **GIVEN** `.repository-hygiene/` contains content other than the expected report
- **WHEN** the agent validates the directory before removal
- **THEN** the agent SHALL refuse to remove the directory
- **AND** the agent SHALL NOT perform broad or forced removal

#### Scenario: External or unsafe path blocks removal
- **GIVEN** the cleanup path is outside the audited repository root or follows an external link
- **WHEN** the agent validates the path
- **THEN** the agent SHALL refuse removal
- **AND** the agent SHALL leave all files in place

### Requirement: Cleanup failure is reported, not hidden

When cleanup cannot be completed, the agent SHALL report the cleanup failure explicitly and SHALL NOT present the cleanup as completed.

#### Scenario: Cleanup failure surfaced
- **GIVEN** the removal of the temporary directory fails
- **WHEN** the agent reports the flow result
- **THEN** the agent SHALL state that cleanup failed
- **AND** the agent SHALL NOT claim that the temporary artifacts were removed

### Requirement: Unrelated files are not modified without a matching finding

During remediation, the agent SHALL NOT modify `AGENTS.md`, `.gitignore`, configuration files, or any file unrelated to a finding unless a matching finding and operational authorization exist. This prohibition SHALL NOT apply to `auditoria.yaml` initialization performed under the target-verification requirement, which is not a remediation action.

#### Scenario: Unrelated file untouched without a finding
- **GIVEN** no finding references a given file
- **WHEN** the agent performs remediation
- **THEN** the agent SHALL NOT modify that file
- **AND** the agent SHALL NOT create or rewrite `AGENTS.md` automatically
