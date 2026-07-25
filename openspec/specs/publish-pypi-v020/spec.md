# Publish PyPI — Versionamento Contínuo

## Purpose

This capability covers the PyPI publication of `repository-hygiene`, including version metadata determined by semantic release, install instructions, workflow template with dynamic version, migration documentation, and automated tagging.

## Requirements

### Requirement: Package version is determined by semantic release
The version in `pyproject.toml` SHALL be determined and updated automatically by the release pipeline based on Conventional Commits since the last tag, rather than being a fixed hardcoded value.

#### Scenario: Version matches pyproject.toml
- **WHEN** the package is built
- **THEN** `repository-hygiene --version` SHALL output the version matching `pyproject.toml`

#### Scenario: Version changes after feat commit merge
- **GIVEN** a `feat:` commit is merged to main
- **WHEN** the release pipeline executes
- **THEN** `pyproject.toml` SHALL be updated with the next semantic version
- **AND** `repository-hygiene --version` SHALL output the new version

### Requirement: README uses PyPI install instructions
The README SHALL instruct users to install via `pip install repository-hygiene` or `uv tool install repository-hygiene`. The README SHALL NOT state that the package is unpublished.

#### Scenario: README has PyPI install command
- **WHEN** a user reads the Installation section
- **THEN** the README SHALL show `pip install repository-hygiene` or `uv tool install repository-hygiene`
- **AND** the README SHALL NOT contain the phrase "não está publicado"

### Requirement: Workflow template installs from PyPI
The generated workflow template SHALL install `repository-hygiene` via `pip install` from PyPI. The version reference SHALL be dynamic, not a hardcoded version string.

#### Scenario: Workflow uses PyPI install with dynamic version
- **WHEN** `repository-hygiene --init .` generates `.github/workflows/repository-hygiene.yml`
- **THEN** the workflow SHALL contain `pip install repository-hygiene`
- **AND** the workflow SHALL NOT contain a hardcoded version like `repository-hygiene==<fixed>`
- **AND** the workflow SHALL NOT contain `git+https://github.com`

### Requirement: Migration guide exists
The README SHALL document how to migrate from `0.1.0` CLI (`audit`, `install`, `update`) to `0.2.0` CLI (`--init`, direct audit, `--install-hook`).

#### Scenario: Migration section present
- **WHEN** a user reads the README
- **THEN** the README SHALL contain a "Migração" section
- **AND** the section SHALL map `audit` → direct call, `install` → `--init`, `update` → removed

### Requirement: Tag created by release pipeline
A Git tag SHALL be created automatically by the release pipeline pointing to the commit that produced the PyPI release.

#### Scenario: Tag created on release
- **WHEN** the release pipeline publishes a new version to PyPI
- **THEN** a tag matching the version SHALL exist in the repository
- **AND** the tag SHALL point to the same commit used for the PyPI build
