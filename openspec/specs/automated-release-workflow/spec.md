# Automated Release Workflow

## Purpose

Automated CI/CD pipeline triggered on push to main that analyzes Conventional Commits, determines next semantic version, generates changelog, creates git tag, builds the package, and publishes to PyPI.

## ADDED Requirements

### Requirement: Release pipeline triggered by push to main
The system SHALL run the release pipeline automatically on every push to the `main` branch.

#### Scenario: Push to main triggers pipeline
- **GIVEN** a commit is pushed to the `main` branch
- **WHEN** the CI workflow starts
- **THEN** the release pipeline SHALL execute

#### Scenario: Push to non-main does not trigger pipeline
- **GIVEN** a commit is pushed to a branch other than `main`
- **WHEN** the CI workflow starts
- **THEN** the release pipeline SHALL NOT execute

### Requirement: Version bump from conventional commits
The system SHALL analyze commit messages since the most recent git tag, determine the next semantic version based on Conventional Commits, and update `pyproject.toml` with the new version. A `feat:` commit SHALL trigger a MINOR bump, a `fix:` commit SHALL trigger a PATCH bump, and a commit containing `!` (breaking change) SHALL trigger a MAJOR bump.

#### Scenario: Feat commit triggers minor bump
- **GIVEN** the current version is `0.3.0`
- **AND** commits since last tag include at least one `feat:` message
- **WHEN** the release pipeline analyzes the commit history
- **THEN** the version in `pyproject.toml` SHALL be updated to `0.4.0`

#### Scenario: Fix commit triggers patch bump
- **GIVEN** the current version is `0.3.0`
- **AND** commits since last tag include only `fix:` messages
- **WHEN** the release pipeline analyzes the commit history
- **THEN** the version in `pyproject.toml` SHALL be updated to `0.3.1`

#### Scenario: Multiple commit types coexist — highest bump wins
- **GIVEN** the current version is `0.3.0`
- **AND** commits since last tag include both `feat:` and `fix:` messages
- **WHEN** the release pipeline analyzes the commit history
- **THEN** the version in `pyproject.toml` SHALL be updated to `0.4.0`

#### Scenario: First release with no prior tags
- **GIVEN** no git tags exist in the repository
- **AND** commits include conventional commit messages
- **WHEN** the release pipeline analyzes the commit history
- **THEN** the version SHALL be determined from all commits in the repository
- **AND** the version in `pyproject.toml` SHALL be updated accordingly

### Requirement: Pipeline skips when no conventional commits found
The system SHALL skip the release when no conventional commits exist since the last tag, producing no version bump, no changelog, and no PyPI upload.

#### Scenario: No conventional commits since last tag
- **GIVEN** all commits since the last tag are non-conventional
- **WHEN** the release pipeline analyzes the commit history
- **THEN** the pipeline SHALL exit successfully without any version change
- **AND** no tag SHALL be created
- **AND** no upload SHALL occur

### Requirement: Changelog generation
The system SHALL generate a `CHANGELOG.md` file from conventional commits since the last release, categorized by commit type (feat, fix, docs, etc.).

#### Scenario: Changelog generated with categorized entries
- **GIVEN** commits since last tag include `feat: add search` and `fix: crash on empty input`
- **WHEN** the release pipeline generates the changelog
- **THEN** `CHANGELOG.md` SHALL contain an entry for the new version
- **AND** the feat entry SHALL appear under a Features section
- **AND** the fix entry SHALL appear under a Fixes section

### Requirement: Git tag creation
The system SHALL create a git tag matching the new version and push both the bump commit and the tag to the remote repository.

#### Scenario: Tag pushed after version bump
- **GIVEN** the version has been bumped from `0.3.0` to `0.4.0`
- **WHEN** the release pipeline pushes changes
- **THEN** a git tag `v0.4.0` SHALL exist in the remote repository
- **AND** the tag SHALL point to the commit that updated `pyproject.toml`

### Requirement: Build and PyPI upload
The system SHALL build the Python package and upload it to PyPI using the `PYPI_TOKEN` secret for authentication.

#### Scenario: Successful build and upload
- **GIVEN** the version has been bumped and a tag has been created
- **WHEN** the build step executes
- **THEN** a wheel and source distribution SHALL be produced in `dist/`
- **AND** the upload step SHALL publish both artifacts to PyPI

#### Scenario: Build fails before upload
- **GIVEN** the version has been bumped and a tag has been created
- **WHEN** the build step encounters an error
- **THEN** the pipeline SHALL fail before reaching the upload step
- **AND** no artifacts SHALL be published to PyPI

### Requirement: PyPI token error handling
The system SHALL fail with a clear error message when the `PYPI_TOKEN` secret is missing or invalid, before attempting any upload.

#### Scenario: Missing PyPI token
- **GIVEN** the `PYPI_TOKEN` secret is not configured
- **WHEN** the pipeline reaches the upload step
- **THEN** the pipeline SHALL fail with an error message indicating the missing secret
