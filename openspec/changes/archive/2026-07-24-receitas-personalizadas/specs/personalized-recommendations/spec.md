## ADDED Requirements

### Requirement: Ingredient-based recommendation ranking
The system SHALL recommend catalog recipes by deterministic coverage of available ingredients, missing ingredients, requested restrictions, and preferences before applying generative synthesis.

#### Scenario: Recipe is mostly available
- **WHEN** the inventory matches most required ingredients of a recipe and no restriction conflicts exist
- **THEN** the recipe is eligible and its result includes matched and missing ingredients

#### Scenario: Recipe conflicts with a restriction
- **WHEN** a recipe contains an ingredient excluded by the person's restriction
- **THEN** the recipe is excluded from eligible recommendations

### Requirement: Explainable recommendation result
The system SHALL return the recipe identity, source, matched ingredients, missing ingredients, and the factors used to rank each recommendation.

#### Scenario: Recommendations are available
- **WHEN** eligible recipes are found
- **THEN** the response presents ranked recipes with their explanation and source reference

### Requirement: Insufficient retrieval handling
The system SHALL state that no sufficient catalog match was found when no recipe meets the minimum confidence or eligibility threshold.

#### Scenario: No adequate recipe exists
- **WHEN** no eligible recipe reaches the configured threshold
- **THEN** the system returns an explicit no-match result and does not fabricate a recipe

### Requirement: Suggested adaptations are separated
The system SHALL label adaptations as suggestions distinct from the official recipe and SHALL NOT persist them as official catalog recipes.

#### Scenario: Person requests an adaptation
- **WHEN** the person asks for a change to a recommended recipe
- **THEN** the response labels the change as a suggestion and retains the original recipe reference
