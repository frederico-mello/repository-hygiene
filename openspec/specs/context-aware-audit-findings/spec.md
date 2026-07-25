# Context-Aware Audit Findings

## Purpose

Reduce false positives in audit results by classifying findings with contextual awareness — distinguishing test fixtures from operational secrets, file-path references from arbitrary strings, and generated artifacts from tracked source.

## Requirements

### Requirement: Contextual finding classification
The auditor MUST classify each detected occurrence using file context and assign a confidence level of `high`, `medium`, or `low` before adding an actionable result.

#### Scenario: Test fixture secret is not an operational secret
- **WHEN** a test fixture writes `senha=admin` into a temporary file under a configured test path
- **THEN** the auditor MUST omit it from high-confidence secret findings or report it only as low confidence

#### Scenario: Operational credential remains actionable
- **WHEN** a tracked application or runtime configuration file contains a credential pattern outside excluded example and fixture contexts
- **THEN** the auditor MUST report a high- or medium-confidence secret finding with file and line evidence

### Requirement: Context-aware path reference detection
The auditor MUST distinguish file-path references from arbitrary strings, versions, commands, module names, URLs, messages, and test fixture names.

#### Scenario: Version and install command are documentation text
- **WHEN** Markdown contains `0.2.0` or `pip install package==0.2.0`
- **THEN** the auditor MUST NOT report either value as a missing file reference

#### Scenario: Broken Markdown link remains detectable
- **WHEN** Markdown contains a relative link whose target does not exist
- **THEN** the auditor MUST report a missing-reference finding with the source path and target

#### Scenario: Temporary fixture path is not repository reference
- **WHEN** test code creates `segredo.txt` or `config.txt` under a temporary directory
- **THEN** the auditor MUST NOT report that filename as a missing repository reference

### Requirement: Heuristic orphan-file reporting
The auditor MUST treat files-without-reference results as heuristic candidates and MUST inspect structural references including imports, workflow paths, entry points, and OpenSpec relationships where applicable.

#### Scenario: Imported module is not orphaned
- **WHEN** a Python file is imported by another tracked module
- **THEN** the auditor MUST NOT report it as an unreferenced file

#### Scenario: Unreferenced planning document is reported as low confidence
- **WHEN** a tracked planning document has no detectable structural or textual reference
- **THEN** the auditor MUST report it as a low-confidence warning with recommendation to review, not as proof of dead content

### Requirement: Generated-artifact classification
The auditor MUST report only untracked paths matching configured generated-artifact patterns and MUST NOT classify tracked source directories as generated artifacts.

#### Scenario: Tracked source directory exists
- **WHEN** `src/repository_hygiene/` is tracked by Git
- **THEN** the auditor MUST NOT report the directory as an artifact outside `.gitignore`

#### Scenario: Untracked cache is not ignored
- **WHEN** an untracked `.ruff_cache/` directory exists and is not covered by `.gitignore` or an explicit artifact policy
- **THEN** the auditor MUST report it with evidence that it is generated and untracked

### Requirement: Contextual workflow permission reporting
The auditor MUST evaluate workflow write permissions against configured allowed scopes and MUST distinguish necessary scoped permissions from broad or dangerous permissions.

#### Scenario: Required issue permission is allowed
- **WHEN** a workflow uses `issues: write` for its configured issue-management operation and the scope is explicitly allowed
- **THEN** the auditor MUST NOT report the permission as excessive

#### Scenario: Broad write permission is unsafe
- **WHEN** a workflow declares `write-all` or an unconfigured broad write scope
- **THEN** the auditor MUST report a high-confidence workflow security warning with the scope and remediation

### Requirement: Confidence-aware audit status
The auditor MUST preserve all reportable findings but MUST fail the audit only for error-severity findings with confidence `high` or `medium`.

#### Scenario: Low-confidence finding only
- **WHEN** an audit contains only low-confidence warnings or errors
- **THEN** the audit status MUST remain successful while the findings remain visible in reports

#### Scenario: Confirmed error exists
- **WHEN** an audit contains at least one high- or medium-confidence error
- **THEN** the audit status MUST be `falha`

### Requirement: Explainable findings
Each contextual finding MUST include evidence describing the matched context and the confidence decision when that information is available.

#### Scenario: Finding includes context evidence
- **WHEN** a detector emits a contextual result
- **THEN** the result MUST contain the existing rule, path, severity, and message fields plus confidence and evidence fields

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
