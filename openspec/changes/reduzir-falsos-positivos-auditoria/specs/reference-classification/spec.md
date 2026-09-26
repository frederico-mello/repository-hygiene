## ADDED Requirements

### Requirement: Classify candidate references before filesystem validation
The auditor MUST classify extracted occurrences as file references, versions, properties, runtime paths, templates, URLs, historical references, or unknown before checking filesystem existence.

#### Scenario: Version is ignored
- **WHEN** a YAML or JSON value is `"1.4.1"`
- **THEN** the auditor classifies it as a version and does not report a missing file

#### Scenario: Structured property is ignored
- **WHEN** a document contains `planningHome.changesDir` or `apply.requires`
- **THEN** the auditor classifies it as a property and does not validate it as a filesystem path

#### Scenario: Template placeholder is ignored
- **WHEN** a value contains `specs/<capability>/spec.md`
- **THEN** the auditor classifies it as a template and does not report it as a missing literal path

### Requirement: Resolve references using repository evidence
The auditor MUST resolve candidates against a shared repository index and distinguish exact, relative, unique basename, ambiguous, and missing results.

#### Scenario: Existing application file has abbreviated name
- **WHEN** a reference names `routes.py` and the repository has one matching `app/routes.py`
- **THEN** the auditor records the candidate resolution and does not report the reference as missing

#### Scenario: Ambiguous basename is not confirmed
- **WHEN** a reference names `routes.py` and multiple repository files have that basename
- **THEN** the auditor marks the result ambiguous rather than treating it as an exact resolution

#### Scenario: Runtime path is not current repository evidence
- **WHEN** a value names `instance/jogos.db` or `unix:/run/gunicorn.sock`
- **THEN** the auditor classifies it as runtime unless explicit configuration marks it as a repository artifact
