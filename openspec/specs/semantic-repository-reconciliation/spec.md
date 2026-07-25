# Semantic Repository Reconciliation

## Purpose

Reconciliar a estrutura do repositório auditado com seus documentos de planejamento (OpenSpec), documentação relacionada (OpenWiki) e grafo de conhecimento (Graphify) para classificar conteúdo excedente, ausente, necessário ou ambíguo e produzir recomendações acionáveis e explicáveis.

## Requirements

### Requirement: Nested repository detection

The auditor SHALL detect directories within the audited tree that contain their own `.git` directory or that structurally resemble a cloned repository. The auditor SHALL classify such directories as accidental clones, intended submodules, or gitignored clones before recommending any action.

#### Scenario: Accidental clone is recommended for removal

- **WHEN** a subdirectory contains a `.git` folder and has no reference in `.gitmodules`, `.gitignore`, or any planning document
- **THEN** the auditor SHALL recommend removal of the nested repository
- **AND** the auditor SHALL NOT recommend adding it to `.gitignore`

#### Scenario: Intended submodule is preserved

- **WHEN** a subdirectory is registered in `.gitmodules`
- **THEN** the auditor SHALL classify it as an intended submodule
- **AND** the auditor SHALL NOT recommend removal or gitignore insertion

#### Scenario: Gitignored clone is not re-reported

- **WHEN** a subdirectory matches an existing `.gitignore` pattern
- **THEN** the auditor SHALL NOT report it as an artifact outside `.gitignore`

### Requirement: Semantic evidence assembly from planning documents

The auditor SHALL read OpenSpec documents in `openspec/specs/` and `openspec/changes/` to assemble evidence about what the repository should contain and SHALL use that evidence to classify files and directories as referenced, planned, unmatched, or surplus.

#### Scenario: File referenced in OpenSpec spec is not orphaned

- **WHEN** a file path appears in any `openspec/specs/**/spec.md`
- **THEN** the auditor SHALL treat the file as structurally referenced
- **AND** the auditor SHALL NOT report it as an unreferenced file

#### Scenario: Directory planned in OpenSpec change is preserved

- **WHEN** a directory matches a path described in an unarchived OpenSpec change
- **THEN** the auditor SHALL classify it as planned content
- **AND** the auditor SHALL NOT recommend removal

#### Scenario: File absent from all planning documents triggers investigation

- **WHEN** a file has no reference in OpenSpec, OpenWiki documentation, or knowledge graph evidence
- **THEN** the auditor SHALL report it as a low-confidence warning
- **AND** the auditor SHALL recommend investigation rather than automatic removal

### Requirement: Cross-source consistency verification

The auditor SHALL identify gaps between what the repository contains, what its OpenSpec documents describe, what its OpenWiki entries document, and what its knowledge graph maps.

#### Scenario: Content present but not documented

- **WHEN** a file or directory exists in the repository but has no entry in OpenSpec or OpenWiki and no knowledge graph node
- **THEN** the auditor SHALL report a documentation gap
- **AND** the auditor SHALL distinguish between surplus content and missing documentation

#### Scenario: Content documented but missing from repository

- **WHEN** an OpenSpec spec or OpenWiki entry references a file that does not exist in the repository
- **THEN** the auditor SHALL report a missing-file reference
- **AND** the auditor SHALL include the source document and the expected path

#### Scenario: Knowledge graph node without repository backing

- **WHEN** the knowledge graph contains a node for a symbol or file not present in the repository
- **THEN** the auditor SHALL report it as stale knowledge
- **AND** the auditor SHALL recommend regenerating the graph

### Requirement: Recommendation taxonomy

The auditor SHALL classify each finding into exactly one recommendation category: remove, preserve, correct, investigate, or accepted-false-positive.

#### Scenario: Accidental content triggers removal recommendation

- **WHEN** a nested repository, orphaned directory, or untracked artifact has no structural or planning-document reference
- **THEN** the auditor SHALL emit a recommendation of `remove`

#### Scenario: False positive triggers acceptance recommendation

- **WHEN** a finding matches a configured exception or an explicit acceptance justification
- **THEN** the auditor SHALL classify it as `accepted-false-positive`
- **AND** the auditor SHALL NOT include it in the remediation queue

#### Scenario: Ambiguous content triggers investigation recommendation

- **WHEN** a file or directory has partial or conflicting evidence
- **THEN** the auditor SHALL classify it as `investigate`
- **AND** the auditor SHALL report the conflicting evidence sources

### Requirement: Workflow intent evaluation

The auditor SHALL evaluate GitHub Actions workflow permissions against the workflow's purpose, trigger events, and effective permission usage rather than against a blanket list of allowed write scopes.

#### Scenario: Workflow with issues-write for issue management is allowed

- **WHEN** a workflow uses `issues: write` and its job steps include issue creation or update operations via `actions/github-script` or the GitHub CLI
- **THEN** the auditor SHALL classify the permission as justified
- **AND** the auditor SHALL NOT report an insecure-workflow warning

#### Scenario: Workflow with write-all and no specific justification

- **WHEN** a workflow declares `write-all` or `permissions: write-all`
- **THEN** the auditor SHALL report a high-confidence insecure-workflow finding
- **AND** the auditor SHALL recommend scoping to the minimum required permissions

#### Scenario: Workflow with contents-write for release creation is allowed

- **WHEN** a workflow uses `contents: write` to create releases or tags as part of its documented purpose
- **THEN** the auditor SHALL classify the permission as justified
- **AND** the auditor SHALL NOT report it as excessive
