## ADDED Requirements

### Requirement: Nested repository context detection

The auditor SHALL detect subdirectories that structurally resemble cloned repositories and SHALL classify them as accidental clones, intended submodules, or gitignored clones. The auditor SHALL NOT treat an accidental clone as a generated artifact to be added to `.gitignore`.

#### Scenario: Nested repo without gitmodule or gitignore reference

- **WHEN** a subdirectory contains a `.git` directory and has no entry in `.gitmodules` or `.gitignore`
- **THEN** the auditor SHALL recommend removal of the nested repository
- **AND** the auditor SHALL NOT recommend a `.gitignore` pattern for it

#### Scenario: Nested repo covered by gitignore

- **WHEN** a subdirectory matches an existing `.gitignore` pattern
- **THEN** the auditor SHALL NOT report it as an artifact outside `.gitignore`

### Requirement: Workflow permission evaluation by purpose

The auditor SHALL evaluate workflow `permissions` blocks against the workflow file's trigger events, job steps, and documented purpose. A write permission that matches the workflow's operational need SHALL NOT be reported as insecure.

#### Scenario: GitHub Actions workflow with justified write permission

- **WHEN** a workflow uses `issues: write` or `contents: write` and its steps perform issue management or release creation
- **THEN** the auditor SHALL classify the permission as justified
- **AND** the auditor SHALL NOT emit an insecure-workflow finding

#### Scenario: Broad write permission without documented need

- **WHEN** a workflow declares `write-all` or unqualified `write` without job-level scoping
- **THEN** the auditor SHALL report a high-confidence insecure-workflow finding

### Requirement: Semantic evidence cross-referencing

The auditor SHALL consult OpenSpec documents, OpenWiki entries, and knowledge graph evidence when evaluating whether a file is unreferenced or a directory is surplus.

#### Scenario: File with OpenSpec reference is not orphaned

- **WHEN** a file path appears in any `openspec/specs/**/spec.md` or `openspec/changes/**/*.md`
- **THEN** the auditor SHALL treat the file as structurally referenced
- **AND** the auditor SHALL NOT report it as an unreferenced file

#### Scenario: Directory matching planning document is preserved

- **WHEN** a directory path matches content described in an unarchived OpenSpec change
- **THEN** the auditor SHALL classify it as planned content
- **AND** the auditor SHALL NOT recommend removal
