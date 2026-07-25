## ADDED Requirements

### Requirement: Skill provisioned on install
The install flow MUST make the `agent-hygiene-flow` OpenCode skill available
inside the target repository so the agent can load it after the flow
completes.

#### Scenario: Skill appears in target repo after install
- **WHEN** the user runs `repository-hygiene install` against a repository
  that does not yet have the skill
- **THEN** the skill's files are present at `<repo>/.opencode/skills/agent-hygiene-flow/SKILL.md`

### Requirement: Skip existing skill by default
The install flow MUST NOT overwrite an already-provisioned skill unless the
user explicitly opts in.

#### Scenario: Existing skill is preserved
- **WHEN** the user runs `repository-hygiene install` against a repository
  that already has a skill at `.opencode/skills/agent-hygiene-flow/`
- **THEN** the existing files are left unchanged
- **AND** the flow reports that the skill already exists

#### Scenario: Existing skill is overwritten with --force
- **WHEN** the user runs `repository-hygiene install --force` against a
  repository that already has a skill at `.opencode/skills/agent-hygiene-flow/`
- **THEN** the existing files are replaced by the bundled version
- **AND** the replacement is reported in the flow output

### Requirement: Dry run reports planned skill provisioning
The install flow MUST report the skill provisioning step under `--dry-run`
without modifying any files.

#### Scenario: Dry run prints the planned operation
- **WHEN** the user runs `repository-hygiene install --dry-run` against a
  repository that does not yet have the skill
- **THEN** the output mentions that the skill would be provisioned
- **AND** no files are written under `.opencode/skills/`

### Requirement: Skill travels with the package version
The skill files shipped to target repositories MUST be the version bundled
with the installed package, so the user can rely on the package version to
identify the skill version.

#### Scenario: Bundle originates from the installed package
- **WHEN** the install flow provisions the skill
- **THEN** the files written to the target repo come from the package's own
  resource directory, not from the skill directory of any other repository
