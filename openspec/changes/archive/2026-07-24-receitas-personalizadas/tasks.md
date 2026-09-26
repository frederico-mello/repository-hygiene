## 1. Project Foundation

- [x] 1.1 Inspect the existing project structure and establish the application, test, and configuration entry points.
- [x] 1.2 Define the canonical recipe, ingredient, source, inventory, and recommendation data models with stable identifiers.
- [x] 1.3 Configure persistence and migrations for recipe versions, normalized ingredients, inventories, and source metadata.

## 2. Recipe Catalog

- [x] 2.1 Implement source ingestion for approved Desafio Vegano recipe pages or fixtures, including required-field validation.
- [x] 2.2 Implement ingredient and recipe normalization while preserving original recipe text and source attribution.
- [x] 2.3 Implement idempotent recipe identity and version updates, retaining prior versions for audit and rollback.
- [x] 2.4 Add lexical, exact, semantic, and structured catalog retrieval behind a single query interface.
- [x] 2.5 Add ingestion and catalog tests covering valid recipes, incomplete sources, duplicate ingestion, changed versions, and source references.

## 3. Ingredient Inventory

- [x] 3.1 Implement inventory create, list, update, and remove operations scoped to a person.
- [x] 3.2 Add curated alias and inflection normalization with original-input preservation and explicit handling of unknown ingredients.
- [x] 3.3 Support optional quantity and unit fields while retaining binary availability when quantity is absent.
- [x] 3.4 Add inventory tests covering lifecycle operations, aliases, unknown ingredients, and quantity-less availability.

## 4. Personalized Recommendations

- [x] 4.1 Implement deterministic eligibility and ranking using ingredient coverage, missing ingredients, restrictions, and preferences.
- [x] 4.2 Implement recommendation responses with recipe identity, source, matched ingredients, missing ingredients, and ranking factors.
- [x] 4.3 Implement minimum-confidence and no-match handling without fabricating recipes.
- [x] 4.4 Add recommendation tests for compatible recipes, restriction conflicts, explainability, and insufficient retrieval.

## 5. Recipe Assistant

- [x] 5.1 Implement conversational request parsing for inventory context, exclusions, and priorities.
- [x] 5.2 Implement grounded response synthesis using only retrieved recipes, inventory data, and explicit preferences.
- [x] 5.3 Add source attribution and response validation to prevent unsupported ingredients, steps, or recipe facts.
- [x] 5.4 Separate adaptation suggestions from official recipes and prevent persisting suggestions as catalog content.
- [x] 5.5 Add assistant tests for explanations, unsupported questions, priority refinement, attribution, and adaptation labeling.

## 6. Quality And Operations

- [x] 6.1 Add observability for ingestion failures, retrieval confidence, no-match responses, source versions, and assistant validation failures.
- [x] 6.2 Add a pilot dataset and evaluation fixtures for retrieval precision, ingredient coverage, attribution, and grounded responses.
- [x] 6.3 Document source permissions, update procedures, rollback of problematic recipe versions, and the criteria for evaluating GraphRAG.
- [x] 6.4 Run the full test suite and verify the first end-to-end flow from inventory submission to cited recommendation.
