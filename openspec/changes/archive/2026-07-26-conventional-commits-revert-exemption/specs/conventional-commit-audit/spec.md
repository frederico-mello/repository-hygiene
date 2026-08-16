## ADDED Requirements

### Requirement: Git revert commits are ignored
The system SHALL NOT validate git revert commits, preventing false positives from `git revert` auto-generated messages. A commit SHALL be considered a revert when its subject line starts with `Revert "`.

#### Scenario: Revert commit skipped
- **GIVEN** a repository with a revert commit `Revert "feat: add OAuth2 support"`
- **WHEN** the `conventional-commits` audit rule executes
- **THEN** no findings SHALL be reported for that revert commit

#### Scenario: Revert with non-conventional inner message still skipped
- **GIVEN** a repository with a revert commit `Revert "added OAuth2"`
- **WHEN** the `conventional-commits` audit rule executes
- **THEN** no findings SHALL be reported for that revert commit

#### Scenario: Non-revert conventional commit still validated
- **GIVEN** a repository with commit `feat: remove broken feature`
- **WHEN** the `conventional-commits` audit rule executes
- **THEN** no findings SHALL be reported for that commit

#### Scenario: Non-revert non-conventional commit still flagged
- **GIVEN** a repository with commit `rolled back the auth changes`
- **WHEN** the `conventional-commits` audit rule executes
- **THEN** a finding SHALL be reported for that commit
