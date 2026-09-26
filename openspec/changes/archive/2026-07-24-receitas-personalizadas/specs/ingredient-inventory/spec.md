## ADDED Requirements

### Requirement: Ingredient inventory management
The system SHALL allow a person to add, list, update, and remove ingredients from their inventory.

#### Scenario: Person adds an ingredient
- **WHEN** the person submits a valid ingredient name
- **THEN** the system stores it associated with that person's inventory

#### Scenario: Person removes an ingredient
- **WHEN** the person removes an ingredient from the inventory
- **THEN** subsequent recommendation requests do not treat that ingredient as available

### Requirement: Ingredient normalization
The system SHALL map recognized aliases and inflection variants to a canonical ingredient while preserving the person's original input for display.

#### Scenario: Alias is recognized
- **WHEN** the person adds a recognized alias of a canonical ingredient
- **THEN** matching uses the canonical ingredient and display retains the original input

#### Scenario: Ingredient is unknown
- **WHEN** the person adds a name with no recognized canonical mapping
- **THEN** the system stores the input as unnormalized and does not silently map it to another ingredient

### Requirement: Optional availability quantity
The system MAY store an optional quantity and unit for an inventory item, and SHALL use binary availability when quantity is absent.

#### Scenario: Quantity is omitted
- **WHEN** an ingredient is stored without quantity
- **THEN** recommendation matching treats the ingredient as available without claiming a quantity match
