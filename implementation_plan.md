# Implementation Plan — Redesign Recommendation Intelligence Architecture

Redesign the recommendation intelligence of the **RazorFlow-AI** e-commerce agent. Replace ad-hoc rule overrides and hardcoded category/product checks with a catalog-driven, multi-stage architecture:

```
User Input → Intent Extraction → Structured Requirements → Context Merge → Product Validation → Recommendation Scoring → Alternative Handling → AI Response / Cart Resolution
```

The application logic strictly enforces product validity, category boundaries, and mandatory constraints before scoring or recommending products. The LLM handles natural intent understanding and response framing, but cannot override validated product outputs.

---

## User Review Required

> [!IMPORTANT]
> - **Catalog-Driven & Dynamic System:** The system will dynamically inspect `catalog.json` at startup to index categories, brands, tags, attributes, and price bounds. No products, categories, or query keywords will be hardcoded in Python files.
> - **Strict Mandatory Validation Before Ranking:** Products are validated against requested category, budget cap, and explicit attributes *before* any ranking occurs. Unvalidated or over-budget products are never passed to the ranking engine or rendered as recommended product cards.
> - **Category Boundary Preservation in Alternatives:** If no exact match exists, alternatives are generated exclusively within the requested product/category. The system will never automatically replace a requested product (e.g. Laptop) with an unrelated category (e.g. Mouse). If the category is not present in the store catalog, it explicitly communicates category unavailability.
> - **Exact Product Resolution for Cart Actions:** Actions (`ADD`, `REMOVE`, `UPDATE`) resolve exact product IDs against current cart items or active recommendation context before mutating cart state.

---

## Proposed Changes

### Backend (`/backend/app`)

#### [NEW] [catalog_registry.py](file:///d:/Khushi/RazorFlow_AI/backend/app/agent/catalog_registry.py)
- Catalog-driven indexer that dynamically analyzes `catalog.json` at startup.
- Indexes unique categories, category synonyms, brand names, attribute keys (RAM, processor, display, storage, color, material, size), feature tags, review themes, and category price floors/ceilings.
- Provides utility methods: `get_matching_category()`, `get_min_category_price()`, `get_known_brands()`, `is_category_in_catalog()`.

#### [NEW] [product_validator.py](file:///d:/Khushi/RazorFlow_AI/backend/app/agent/product_validator.py)
- Application logic for strict product candidate validation (Zero LLM Hallucinations).
- Validates catalog items against Mandatory Constraints:
  1. **Category Match:** Product must match requested category / head noun.
  2. **Budget Fit:** Product price must be <= max_price.
  3. **Explicit Attributes:** Product must satisfy explicitly requested attributes (brand, color, size, material, specs, required features).
- Returns `ValidationResult` with `exact_matches` (validated candidates), `same_category_products` (candidate pool for alternatives), and constraint conflict flags (`BUDGET_EXCEEDED`, `ATTRIBUTE_MISMATCH`, `MULTI_CONSTRAINT`, `CATEGORY_UNAVAILABLE`).

#### [NEW] [alternative_handler.py](file:///d:/Khushi/RazorFlow_AI/backend/app/agent/alternative_handler.py)
- Executes intelligent alternative handling when `exact_matches` is empty.
- Preserves requested category boundary strictly.
- Handles:
  - **Budget Relaxation:** Identifies closest available products in SAME category starting at category price floor (+price delta).
  - **Attribute Relaxation:** Identifies same-category products within budget, explicitly highlighting relaxed attributes.
  - **Multi-Constraint Conflict:** Presents structured choices (Budget vs Attribute adjustment).
  - **Category Unavailability:** Informs user if category is not in store inventory and lists available store categories without returning unrelated product cards.

#### [MODIFY] [ranking_engine.py](file:///d:/Khushi/RazorFlow_AI/backend/app/agent/ranking_engine.py)
- Remove hardcoded category checks (`["kurta set", "laptops", "bag", "mouse"]`) and rely on `CatalogRegistry`.
- Refactor `rank_catalog` to score ONLY validated products across weighted dimensions:
  1. Requirement & Keyword Relevance
  2. Use Case Alignment (matching coding, gaming, battery, etc.)
  3. Specification Match
  4. Bayesian Rating & Review Volume
  5. Value for Money & Budget Fit
- Output structured ranking results with natural language explanations.

#### [MODIFY] [ai_service.py](file:///d:/Khushi/RazorFlow_AI/backend/app/services/ai_service.py)
- Update `extract_structured_intent` to use `CatalogRegistry` for category and brand detection.
- Remove hardcoded list of categories, brands, and multi-word keywords.
- Enforce output schema containing `intent_type`, `category`, `attributes`, `budget`, `use_case`, `quantity`.

#### [MODIFY] [context_manager.py](file:///d:/Khushi/RazorFlow_AI/backend/app/agent/context_manager.py)
- Enhance conversational state management to persist extracted requirements across multi-turn queries.
- Detect category switches dynamically via `CatalogRegistry`.
- Preserve active recommendation context and selected product identity for follow-up questions or voice conversations.

#### [MODIFY] [cart_intent_detector.py](file:///d:/Khushi/RazorFlow_AI/backend/app/agent/cart_intent_detector.py)
- Remove hardcoded model names (`["thinkpad", "zenbook", "macbook"]`) and query `CatalogRegistry`.
- Resolve exact target product from current cart (for REMOVE/UPDATE) or active recommendation context (for ADD).
- Request explicit clarification when query is ambiguous and no active context exists.

#### [MODIFY] [graph.py](file:///d:/Khushi/RazorFlow_AI/backend/app/agent/graph.py)
- Orchestrate the complete redesigned 7-stage pipeline in `process_message`:
  1. Intent Extraction (`ai_service` + `ranking_engine`)
  2. Context Merge (`context_manager`)
  3. Product Validation (`product_validator`)
  4. Recommendation Scoring (`ranking_engine`)
  5. Alternative Handling (`alternative_handler`)
  6. Cart Action & Guardrail Check (`cart_intent_detector` + Razorpay Service)
  7. Response Formatting & State Update
- Ensure payment guardrails remain deterministic.

---

### Tests (`/backend/tests`)

#### [MODIFY] [test_agent_scenarios.py](file:///d:/Khushi/RazorFlow_AI/backend/tests/test_agent_scenarios.py)
- Update and add comprehensive unit test cases for:
  - Exact category & attribute intent parsing
  - Validation before ranking
  - Category boundary preservation during alternative suggestions
  - Budget relaxation notices
  - Cart action product resolution
  - Out-of-catalog category handling

---

## Verification Plan

### Automated Tests
- Run Python unit test suite:
  ```powershell
  python -m unittest discover -s backend/tests -p "test_*.py"
  ```
- All 43+ scenario tests must pass clean with 0 failures.

### Manual & Voice Verification
1. **Valid Recommendation Flow:**
   - Query: `"Find laptops for coding under ₹60,000"` -> Verify ZenBook Pro 14 / ThinkPad E14 returned, price <= 60,000.
2. **Category Boundary & Out-of-Budget Alternative:**
   - Query: `"I need a laptop for coding under ₹30,000"` -> Verify response states budget limitation, suggests closest Laptop starting at ₹54,990, and does NOT return non-laptop items.
3. **Out-of-Catalog Category Handling:**
   - Query: `"I need a watch"` or `"blue kurta set for womens"` -> Verify agent states category is unavailable in catalog and returns empty products array.
4. **Product Category Disambiguation:**
   - Query: `"I need a laptop carry bag"` -> Verify Accessories category (sleeve/bag) returned, NOT laptops.
5. **Exact Cart Action Resolution:**
   - Query: `"Add the recommended laptop to my cart"` -> Verify exact product ID from recommendation context is added.
   - Query: `"Take out the mouse"` -> Verify exact mouse product is removed from cart.
6. **Multi-Turn Context Persistence:**
   - Turn 1: `"I need a laptop"` -> Turn 2: `"I also need a carry bag"` -> Verify Turn 2 returns laptop bag/sleeve.
