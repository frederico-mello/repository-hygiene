# skill-provisioning Specification

## Purpose
This capability provisions the skill and configuration files needed by the hygiene flow into every supported agent root of a target repository through the install command, without caring which agent the repository belongs to. Installation selects destinations automatically from the roots present, can be narrowed explicitly, preserves already-provisioned copies unless overwrite is requested, and reports planned work in dry-run mode. The shipped files always match the installed package version, and the same set of agent roots defines what counts as repository source during audits and as trigger paths in the generated workflow.

## Requirements

### Requirement: Skill provisioned on install
The install flow MUST make the `agent-hygiene-flow` skill available inside the target repository for every selected agent root so the agent can load it after the flow completes. Selected roots default to every supported agent root present in the target repository (`.opencode`, `.kilocode`, `.kilo`, `.omp`, `.hermes`), fall back to `.opencode` when none is present, and MAY be restricted explicitly with `--agents`.

#### Scenario: Skill appears in target repo after install
- **WHEN** the user runs `repository-hygiene install` against a repository that contains no supported agent root and does not yet have the skill
- **THEN** the skill's files are present at `<repo>/.opencode/skills/agent-hygiene-flow/SKILL.md`

#### Scenario: Skill provisioned into every present agent root
- **WHEN** the user runs `repository-hygiene install` against a repository that contains `.omp/` and `.hermes/`
- **THEN** the skill's files are present at `<repo>/.omp/skills/agent-hygiene-flow/SKILL.md`
- **AND** the skill's files are present at `<repo>/.hermes/skills/agent-hygiene-flow/SKILL.md`

#### Scenario: Explicit agent selection restricts destinations
- **WHEN** the user runs `repository-hygiene install --agents opencode,kilo` against a repository that contains all supported agent roots
- **THEN** the skill is provisioned under `.opencode/skills/` and `.kilo/skills/`
- **AND** no skill directory is created under the unselected agent roots

### Requirement: Skip existing skill by default
The install flow MUST NOT overwrite an already-provisioned skill in any selected destination unless the user explicitly opts in. Existence is evaluated per destination, so a missing destination is still provisioned while an existing one is preserved.

#### Scenario: Existing skill is preserved
- **WHEN** the user runs `repository-hygiene install` against a repository that already has a skill at `.opencode/skills/agent-hygiene-flow/`
- **THEN** the existing files are left unchanged
- **AND** the flow reports that the skill already exists

#### Scenario: Existing skill is overwritten with --force
- **WHEN** the user runs `repository-hygiene install --force` against a repository that already has a skill at `.opencode/skills/agent-hygiene-flow/`
- **THEN** the existing files are replaced by the bundled version
- **AND** the replacement is reported in the flow output

#### Scenario: Destinations are skipped independently
- **WHEN** the user runs `repository-hygiene install` against a repository where `.opencode/skills/agent-hygiene-flow/` exists but no skill exists under `.omp/`
- **THEN** the existing `.opencode` skill is left unchanged
- **AND** the skill is created at `<repo>/.omp/skills/agent-hygiene-flow/SKILL.md`

### Requirement: Dry run reports planned skill provisioning
The install flow MUST report the skill provisioning step under `--dry-run` without modifying any files, listing every selected destination.

#### Scenario: Dry run prints the planned operation
- **WHEN** the user runs `repository-hygiene install --dry-run` against a repository that does not yet have the skill
- **THEN** the output mentions that the skill would be provisioned at each selected destination, including `.opencode/skills/agent-hygiene-flow` when `.opencode` is selected
- **AND** no files are written under any agent skills directory

### Requirement: Skill travels with the package version
The skill files shipped to target repositories MUST be the version bundled
with the installed package, so the user can rely on the package version to
identify the skill version.

#### Scenario: Bundle originates from the installed package
- **WHEN** the install flow provisions the skill
- **THEN** the files written to the target repo come from the package's own
  resource directory, not from the skill directory of any other repository

### Requirement: Supported agent roots are audit scope
The auditor MUST treat every supported agent root as repository source: files under `.opencode/`, `.kilocode/`, `.kilo/`, `.omp/`, and `.hermes/` are not classified as untracked artifacts, and their agent command, openspec-skill, and workflow directories are exempt from missing-reference enforcement the same way `.opencode/commands/` and `.opencode/skills/openspec-` are today.

#### Scenario: Agent directory is source, not artifact
- **WHEN** the audit runs against a repository containing untracked files under `.omp/`
- **THEN** those files are not reported by `untracked_artifacts`

#### Scenario: Agent command and openspec skill references are not enforced
- **WHEN** a file under `.omp/commands/`, `.kilo/commands/`, `.kilocode/workflows/`, or `.hermes/skills/openspec-` references a path that does not exist
- **THEN** the auditor does not report it as a missing reference

#### Scenario: Provisioned hygiene skill references stay enforced
- **WHEN** `.opencode/skills/agent-hygiene-flow/SKILL.md` references a path that does not exist
- **THEN** the auditor reports the missing reference

### Requirement: Generated workflow triggers cover agent directories
The generated GitHub Actions workflow MUST include path triggers for every supported agent root in both the `push` and `pull_request` filters, so a change to any agent's configuration re-runs the audit.

#### Scenario: Change under an agent root triggers the workflow
- **WHEN** a commit modifies files under `.kilocode/` or `.hermes/`
- **THEN** the workflow's `push` path filters match the changed paths
- **AND** the workflow's `pull_request` path filters match the changed paths
