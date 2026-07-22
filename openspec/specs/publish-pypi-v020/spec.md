## Purpose

This capability covers the PyPI publication of `repository-hygiene` version `0.2.0`, including version metadata, install instructions, workflow template, migration documentation, and tagging.

## Requirements

### Requirement: Package version is 0.2.0
The system SHALL publish version `0.2.0` of `repository-hygiene` to PyPI. The version in `pyproject.toml` SHALL be `0.2.0`.

#### Scenario: Version matches pyproject.toml
- **WHEN** the package is built
- **THEN** `repository-hygiene --version` outputs `repository-hygiene 0.2.0`

### Requirement: README uses PyPI install instructions
The README SHALL instruct users to install via `pip install repository-hygiene` or `uv tool install repository-hygiene`. The README SHALL NOT state that the package is unpublished.

#### Scenario: README has PyPI install command
- **WHEN** a user reads the Installation section
- **THEN** the README SHALL show `pip install repository-hygiene` or `uv tool install repository-hygiene`
- **AND** the README SHALL NOT contain the phrase "não está publicado"

### Requirement: Workflow template installs from PyPI
The generated workflow template SHALL install `repository-hygiene==0.2.0` via `pip install` from PyPI, not from a Git URL.

#### Scenario: Workflow uses PyPI install
- **WHEN** `repository-hygiene --init .` generates `.github/workflows/repository-hygiene.yml`
- **THEN** the workflow SHALL contain `pip install repository-hygiene==0.2.0`
- **AND** the workflow SHALL NOT contain `git+https://github.com`

### Requirement: Migration guide exists
The README SHALL document how to migrate from `0.1.0` CLI (`audit`, `install`, `update`) to `0.2.0` CLI (`--init`, direct audit, `--install-hook`).

#### Scenario: Migration section present
- **WHEN** a user reads the README
- **THEN** the README SHALL contain a "Migração" section
- **AND** the section SHALL map `audit` → direct call, `install` → `--init`, `update` → removed

### Requirement: Tag v0.2.0 matches published package
A Git tag `v0.2.0` SHALL be created pointing to the commit that produced the PyPI release.

#### Scenario: Tag exists
- **WHEN** the package is published on PyPI
- **THEN** a tag `v0.2.0` SHALL exist in the repository
- **AND** the tag SHALL point to the same commit used for the PyPI build
