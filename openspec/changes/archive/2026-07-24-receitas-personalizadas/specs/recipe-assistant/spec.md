## ADDED Requirements

### Requirement: Grounded recipe conversation
The assistant SHALL answer recipe questions using only retrieved catalog content, inventory data, and explicitly identified user preferences.

#### Scenario: Assistant explains a recommendation
- **WHEN** the person asks why a recipe was recommended
- **THEN** the assistant explains the matched and missing ingredients using the recommendation data

#### Scenario: Assistant lacks supporting content
- **WHEN** the question cannot be answered from retrieved recipes or the person's data
- **THEN** the assistant states the limitation instead of inventing recipe facts

### Requirement: Source attribution in assistant responses
The assistant SHALL include the recipe identity and source reference whenever it discusses an official catalog recipe.

#### Scenario: Official recipe is discussed
- **WHEN** the assistant describes ingredients or preparation from a catalog recipe
- **THEN** the response includes the recipe's source reference

### Requirement: Conversational preference handling
The assistant SHALL use explicit conversational constraints such as available ingredients, exclusions, and desired priorities to request or refine recommendations.

#### Scenario: Person prioritizes speed
- **WHEN** the person asks for the fastest option among compatible recipes
- **THEN** the assistant applies that priority to the eligible catalog results and explains the selection
