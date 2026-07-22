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
