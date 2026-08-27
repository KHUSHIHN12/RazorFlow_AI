import re
from typing import List, Dict, Any, Optional
from app.agent.catalog_registry import catalog_registry

class ValidationResult:
    def __init__(self,
                 fallback_level: str,
                 exact_matches: List[Dict[str, Any]],
                 same_category_products: List[Dict[str, Any]],
                 category_exists: bool,
                 min_category_price: float = 0.0,
                 price_delta: float = 0.0,
                 missing_attributes: List[str] = None):
        self.fallback_level = fallback_level
        self.exact_matches = exact_matches
        self.same_category_products = same_category_products
        self.category_exists = category_exists
        self.min_category_price = min_category_price
        self.price_delta = price_delta
        self.missing_attributes = missing_attributes or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "fallback_level": self.fallback_level,
            "exact_matches": self.exact_matches,
            "same_category_products": self.same_category_products,
            "category_exists": self.category_exists,
            "min_category_price": self.min_category_price,
            "price_delta": self.price_delta,
            "missing_attributes": self.missing_attributes
        }

class ProductValidator:
    """
    Strict Application Logic for Product Candidate Validation.
    Executes BEFORE ranking or recommending products.
    Zero LLM Hallucinations — grounded strictly in catalog schema.
    """

    @classmethod
    def validate_catalog(cls, catalog: List[Dict[str, Any]], intent: Dict[str, Any]) -> ValidationResult:
        requested_cat = intent.get("category")
        head_noun = intent.get("head_noun")
        budget = intent.get("max_price")
        brand = intent.get("brand")
        color = intent.get("color")
        size = intent.get("size")
        material = intent.get("material")
        req_features = intent.get("required_features", [])

        target_cat = head_noun or requested_cat

        # Stage 1: Category & Product Boundary Isolation
        if target_cat and not catalog_registry.is_category_in_catalog(target_cat):
            return ValidationResult(
                fallback_level="no_category",
                exact_matches=[],
                same_category_products=[],
                category_exists=False
            )

        same_category_products = []
        for prod in catalog:
            prod_cat = prod.get("category", "").lower()
            prod_name = prod.get("name", "").lower()
            prod_desc = prod.get("description", "").lower()
            prod_tags = [t.lower() for t in prod.get("tags", [])]
            prod_corpus = f"{prod_name} {prod_desc} {' '.join(prod_tags)}"

            if target_cat:
                t_lower = target_cat.lower().strip()

                # Dynamic disambiguation for sub-categories
                if t_lower in ["laptop", "notebook", "macbook"]:
                    if prod_cat != "laptops" and not any(l in prod_name for l in ["zenbook", "thinkpad", "macbook", "legion"]):
                        continue
                    if any(acc in prod_name for acc in ["sleeve", "bag", "cooling pad", "cooler", "hub", "mouse", "keyboard"]):
                        continue
                elif t_lower in ["bag", "sleeve", "case", "pouch", "backpack", "laptop bag", "carry bag"]:
                    if prod_cat != "accessories" or not any(b in prod_name or b in prod_corpus for b in ["bag", "sleeve", "case", "pouch", "backpack"]):
                        continue
                elif t_lower in ["mouse", "mice", "wireless mouse", "gaming mouse"]:
                    if prod_cat != "accessories" or not ("mouse" in prod_name or "mice" in prod_name or "mouse" in prod_tags):
                        continue
                elif t_lower in ["keyboard", "keycaps", "mechanical keyboard"]:
                    if prod_cat != "accessories" or not ("keyboard" in prod_name or "keycaps" in prod_name):
                        continue
                elif t_lower in ["cooler", "cooling", "cooling pad"]:
                    if prod_cat != "accessories" or not ("cooler" in prod_name or "cooling" in prod_name or "cooling pad" in prod_corpus):
                        continue
                elif t_lower in ["hub", "dongle", "adapter", "usb-c hub"]:
                    if prod_cat != "accessories" or not ("hub" in prod_name or "dongle" in prod_name or "adapter" in prod_name):
                        continue
                elif t_lower in ["audio", "headphone", "headphones", "headset", "earphone", "earbuds"]:
                    if prod_cat != "audio" and not any(a in prod_name for a in ["headphone", "headphones", "headset", "earphone", "earbuds", "acoustix"]):
                        continue
                elif t_lower in ["monitor", "display", "screen"]:
                    if prod_cat != "monitors" and not any(m in prod_name for m in ["monitor", "display", "screen"]):
                        continue
                else:
                    matched_cat = catalog_registry.get_matching_category(t_lower)
                    if matched_cat and prod_cat != matched_cat.lower():
                        continue
                    elif not matched_cat:
                        if t_lower not in prod_cat and t_lower not in prod_name and t_lower not in prod_corpus:
                            continue

            same_category_products.append(prod)

        if not same_category_products:
            return ValidationResult(
                fallback_level="no_category",
                exact_matches=[],
                same_category_products=[],
                category_exists=False
            )

        # Stage 2: Validate Candidates against Budget and Explicit Attributes
        exact_matches = []
        all_missing_attributes = []
        min_cat_price = min(float(p.get("price", 0)) for p in same_category_products)
        price_delta = (min_cat_price - budget) if (budget is not None and min_cat_price > budget) else 0.0

        for prod in same_category_products:
            prod_corpus = f"{prod.get('name', '')} {prod.get('description', '')} {' '.join(prod.get('tags', []))} {str(prod.get('specs', {}))}".lower()

            missing = []
            if brand and not re.search(r'\b' + re.escape(brand.lower()) + r'\b', prod_corpus):
                missing.append(f"brand '{brand}'")
            if color and not re.search(r'\b' + re.escape(color.lower()) + r'\b', prod_corpus):
                missing.append(f"color '{color}'")
            if size and not re.search(r'\b' + re.escape(size.lower()) + r'\b', prod_corpus):
                missing.append(f"size '{size}'")
            if material and not re.search(r'\b' + re.escape(material.lower()) + r'\b', prod_corpus):
                missing.append(f"material '{material}'")

            for feat in req_features:
                if not re.search(r'\b' + re.escape(feat.lower()) + r'\b', prod_corpus):
                    missing.append(f"feature '{feat}'")

            price = float(prod.get("price", 0))
            budget_violated = (budget is not None) and (price > budget)

            if not missing and not budget_violated:
                exact_matches.append(prod)
            else:
                for m in missing:
                    if m not in all_missing_attributes:
                        all_missing_attributes.append(m)

        # Stage 3: Determine Validation Status / Fallback Level
        has_attr_conflict = len(all_missing_attributes) > 0
        has_budget_conflict = price_delta > 0 or (budget is not None and all(float(p.get("price", 0)) > budget for p in same_category_products))

        if exact_matches:
            fallback_level = "exact_match"
        elif has_attr_conflict and has_budget_conflict:
            fallback_level = "multi_constraint"
        elif has_attr_conflict:
            fallback_level = "relaxed_attributes"
        elif has_budget_conflict:
            fallback_level = "relaxed_budget"
        else:
            fallback_level = "no_category"

        return ValidationResult(
            fallback_level=fallback_level,
            exact_matches=exact_matches,
            same_category_products=same_category_products,
            category_exists=True,
            min_category_price=min_cat_price,
            price_delta=price_delta,
            missing_attributes=all_missing_attributes
        )

product_validator = ProductValidator()
