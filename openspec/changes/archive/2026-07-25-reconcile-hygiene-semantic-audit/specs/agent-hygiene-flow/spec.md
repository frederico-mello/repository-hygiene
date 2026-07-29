## ADDED Requirements

### Requirement: Remediation taxonomy distinguishes removal from gitignore

The agent SHALL distinguish between content that must be removed (accidental clones, orphaned content with no references) and content that must be covered by `.gitignore` (generated artifacts, caches, build outputs). The agent SHALL NOT add accidental content to `.gitignore` as a substitute for removal.

#### Scenario: Accidental clone triggers removal not gitignore

- **WHEN** an audit finding identifies a nested repository with no structural or planning-document reference
- **THEN** the agent SHALL remediate by removing the nested directory
- **AND** the agent SHALL NOT add a `.gitignore` pattern for it

#### Scenario: Generated artifact triggers gitignore pattern

- **WHEN** an audit finding identifies a generated directory such as `.ruff_cache/` or `__pycache__/`
- **THEN** the agent SHALL remediate by adding the pattern to `.gitignore`
- **AND** the agent SHALL NOT delete the directory if it may be regenerated

### Requirement: Accepted false positives are documented before flow proceeds

The agent SHALL accept a finding as a false positive only through explicit user decision. The agent SHALL record the justification, the finding key, and the acceptance date. An accepted false positive SHALL NOT block the flow and SHALL NOT trigger remediation.

#### Scenario: User accepts a workflow permission as necessary

- **WHEN** a workflow permission finding is identified as necessary for GitHub Actions operation and the user explicitly accepts it
- **THEN** the agent SHALL record the acceptance with justification
- **AND** the agent SHALL proceed with the flow without treating the finding as unresolved

#### Scenario: Unaccepted finding blocks the flow

- **WHEN** a finding remains without user acceptance or remediation
- **THEN** the agent SHALL terminate the flow as blocked
- **AND** the agent SHALL present the residual finding to the user

### Requirement: Semantic evidence informs remediation choice

The agent SHALL cross-reference OpenSpec documents, OpenWiki entries, and knowledge graph evidence before selecting a remediation action for findings related to unreferenced files, surplus directories, or undocumented content.

#### Scenario: Content with semantic evidence is not removed

- **WHEN** a file or directory has references in OpenSpec specs, OpenSpec changes, OpenWiki documentation, or knowledge graph nodes
- **THEN** the agent SHALL classify the content as preserved
- **AND** the agent SHALL NOT recommend removal

#### Scenario: Content without any evidence is recommended for investigation

- **WHEN** a file or directory has no reference in any semantic source
- **THEN** the agent SHALL recommend investigation before removal
- **AND** the agent SHALL NOT remove the content automatically

## MODIFIED Requirements

### Requirement: Each rule maps to a remediation action and blocking severity

The skill SHALL document a triage mapping from each audit rule (`segredos_rastreados`, `links_internos_quebrados`, `referencias_inexistentes`, `artefatos_fora_gitignore`, `gitkeep_sem_conteudo`, `arquivos_sem_referencia`, `documentacao_desatualizada`, `configuracao_sem_integracao`, `openspec_parada`, `workflows_inseguros`) to the expected remediation action and to whether that severity blocks (`error`) or only informs (`warning`). The severities recorded in the matrix SHALL match the severities emitted by the auditor and SHALL NOT be redefined by the skill.

Remediation actions SHALL include at minimum: remove, add-to-gitignore, fix-reference, update-documentation, add-ci-integration, archive-change, scope-permissions, investigate, and accept-false-positive. The `artefatos_fora_gitignore` rule SHALL distinguish between generated artifacts (recommend add-to-gitignore) and accidental content (recommend remove). The `workflows_inseguros` rule SHALL distinguish between unjustified broad permissions (recommend scope-permissions) and justified operational permissions (recommend accept-false-positive).

#### Scenario: Rule maps to a remediation action

- **GIVEN** the skill documents the triage matrix
- **WHEN** the agent encounters a finding for any documented rule
- **THEN** the matrix SHALL provide an expected remediation action for that rule
- **AND** the matrix SHALL state whether the rule's severity blocks or informs
- **BUT** the matrix SHALL NOT redefine a severity different from the one emitted by the auditor

#### Scenario: Accidental content triggers removal action

- **GIVEN** an `artefatos_fora_gitignore` finding identifies a nested repository with no structural reference
- **WHEN** the agent consults the triage matrix
- **THEN** the remediation action SHALL be `remove`, not `add-to-gitignore`

#### Scenario: Justified workflow permission triggers acceptance action

- **GIVEN** a `workflows_inseguros` finding identifies a write permission that matches the workflow's documented purpose
- **WHEN** the agent consults the triage matrix
- **THEN** the remediation action SHALL be `accept-false-positive`
- **AND** the agent SHALL record the justification before proceeding
