## ADDED Requirements

### Requirement: Recipe source ingestion
The system SHALL ingest recipes from the approved Desafio Vegano sources and preserve the original source URL, title, ingredients, preparation steps, portions, and collection timestamp.

#### Scenario: Valid recipe is ingested
- **WHEN** an approved source contains a recipe with required fields
- **THEN** the system stores the normalized recipe and its source metadata

#### Scenario: Source recipe is incomplete
- **WHEN** extraction cannot obtain a required recipe field
- **THEN** the system records an ingestion failure for review and does not invent the missing value

### Requirement: Idempotent recipe versioning
The system SHALL identify a recipe by a stable source identity and SHALL update its version on re-ingestion without creating duplicate recipes.

#### Scenario: Unchanged recipe is re-ingested
- **WHEN** the same source is processed again with unchanged content
- **THEN** the system keeps one recipe identity and records no duplicate

#### Scenario: Recipe content changes
- **WHEN** the same source is processed with changed content
- **THEN** the system stores the new version while retaining the previous version for audit or rollback

### Requirement: Recipe retrieval
The system SHALL support exact, lexical, semantic, and structured retrieval of recipes using indexed recipe content and normalized ingredient data.

#### Scenario: User searches by ingredient
- **WHEN** a query includes a normalized ingredient
- **THEN** the system returns recipes containing that ingredient, ordered by the applicable relevance rules

#### Scenario: Recipe result is displayed
- **WHEN** a recipe is returned from the catalog
- **THEN** the result includes its source identifier and URL
