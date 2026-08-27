import json
import re
from typing import Dict, Any, List, Optional
from app.agent.catalog_registry import catalog_registry

class CommerceIntentResolver:
    """
    Dedicated LLM-Based Commerce Intent Resolution Layer.
    
    Converts natural-language user requests into a predictable, structured JSON intent schema.
    
    Strict Rules:
    - Does NOT select or recommend products.
    - Does NOT invent products or prices.
    - Does NOT change requested product type or category.
    - Does NOT relax user budget.
    - Does NOT choose alternatives or override catalog data.
    
    Application logic remains the final authority for product validity.
    """

    SYSTEM_PROMPT = """
You are a precise Commerce Intent Resolution Engine for RazorFlow AI e-commerce store.
Your ONLY role is to analyze customer text and extract a structured JSON intent.

STRICT RULES:
1. NEVER select, recommend, or suggest specific product items.
2. NEVER invent prices, products, or fake items.
3. Extract exact product_type (e.g., 'laptop', 'mouse', 'keyboard', 'sleeve', 'bag', 'headphone', 'monitor', 'cooler', 'hub').
4. Extract exact category from store catalog ('Laptops', 'Accessories', 'Audio', 'Monitors').
5. Extract budget limit max_price as a number if mentioned (e.g. 60000.0 for 'under 60k').
6. Extract explicit attributes: brand, color, gender, size, material, required_features.
7. Extract use_case (e.g., 'coding', 'gaming', 'office', 'travel').
8. Classify all explicit constraints into explicit_hard_constraints.
9. Detect requested_cart_action: action ('NONE', 'ADD', 'REMOVE', 'UPDATE', 'VIEW', 'CHECKOUT'), target_product_query, quantity.

Return ONLY valid JSON matching this schema:
{
  "product_type": "string or null",
  "category": "string or null",
  "budget": {
    "max_price": number or null,
    "currency": "INR"
  },
  "attributes": {
    "brand": "string or null",
    "color": "string or null",
    "gender": "string or null",
    "size": "string or null",
    "material": "string or null",
    "required_features": ["string"]
  },
  "use_case": "string or null",
  "explicit_hard_constraints": ["string"],
  "optional_constraints": ["string"],
  "requested_cart_action": {
    "action": "NONE|ADD|REMOVE|UPDATE|VIEW|CHECKOUT",
    "target_product_query": "string or null",
    "quantity": number
  }
}
"""

    @classmethod
    def resolve_intent(cls, user_message: str, use_llm: bool = False, api_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Main entry point for Commerce Intent Resolution.
        Tries Gemini LLM if available and enabled, falling back to deterministic parser.
        """
        if use_llm and api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = f"{cls.SYSTEM_PROMPT}\n\nCustomer Request: \"{user_message}\"\n\nJSON Output:"
                res = model.generate_content(prompt)
                txt = res.text.strip()
                if txt.startswith("```json"):
                    txt = txt[7:]
                if txt.endswith("```"):
                    txt = txt[:-3]
                parsed = json.loads(txt.strip())
                return cls._normalize_structured_intent(parsed, user_message)
            except Exception:
                pass

        # Deterministic Commerce Intent Extractor (Catalog-Driven & NLP Schema)
        return cls.deterministic_resolve(user_message)

    @classmethod
    def deterministic_resolve(cls, user_text: str) -> Dict[str, Any]:
        text_lower = user_text.lower().strip()

        # 1. Budget extraction
        max_price = None
        price_match = re.search(r'(?:under|below|less than|within|max|upto|up to|budget|around|@)\s*₹?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(k|lakh)?', text_lower)
        if price_match:
            val = float(price_match.group(1).replace(',', ''))
            unit = price_match.group(2)
            if unit == 'k':
                val *= 1000
            elif unit == 'lakh':
                val *= 100000
            max_price = val

        # 2. Attributes extraction
        color = None
        for c in ["red", "blue", "green", "black", "white", "silver", "gray", "grey", "pink"]:
            if re.search(r'\b' + c + r'\b', text_lower):
                color = c
                break

        gender = None
        if any(w in text_lower for w in ["women", "womens", "women's", "female", "lady", "ladies"]):
            gender = "female"
        elif any(w in text_lower for w in ["men", "mens", "men's", "male"]):
            gender = "male"

        size = None
        size_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:inch|\")?', text_lower)
        if size_match and size_match.group(1) in ["13.3", "13.6", "14", "15.6", "17.3", "27"]:
            size = size_match.group(1)

        brand = catalog_registry.detect_brand(text_lower)

        material = None
        for mat in ["leather", "neoprene", "aluminum", "aluminium", "plastic", "cotton", "mesh", "foam"]:
            if re.search(r'\b' + mat + r'\b', text_lower):
                material = mat
                break

        features = []
        for feat in ["wireless", "anc", "noise cancelling", "4k", "oled", "mechanical", "water-resistant", "water resistant", "ergonomic", "bluetooth", "144hz", "vertical"]:
            if feat in text_lower:
                features.append(feat)

        use_case = None
        for uc in ["coding", "programming", "gaming", "office", "travel", "student", "developer", "data science", "ai development"]:
            if uc in text_lower:
                use_case = uc
                break

        # 3. Product Type & Category Resolution via Dynamic Extraction
        from app.services.ai_service import ai_service
        product_type = ai_service._extract_dynamic_category(text_lower)
        category = catalog_registry.get_macro_category(product_type) if product_type else catalog_registry.get_matching_category(text_lower)
        if not category and product_type:
            category = product_type

        # 4. Cart Action Resolution
        cart_action = "NONE"
        target_query = None
        qty = 1

        if any(k in text_lower for k in ["add to cart", "put in cart", "add the", "add this"]):
            cart_action = "ADD"
            target_query = text_lower
        elif any(k in text_lower for k in ["remove", "delete", "take out"]):
            cart_action = "REMOVE"
            target_query = text_lower
        elif any(k in text_lower for k in ["change quantity", "update quantity", "set quantity"]):
            cart_action = "UPDATE"
            target_query = text_lower
        elif any(k in text_lower for k in ["view cart", "show cart", "whats in cart", "my cart"]):
            cart_action = "VIEW"
        elif any(k in text_lower for k in ["checkout", "pay", "buy now"]):
            cart_action = "CHECKOUT"

        # 5. Build Explicit Hard Constraints List
        hard_constraints = []
        if product_type or category: hard_constraints.append("category")
        if max_price is not None: hard_constraints.append("max_price")
        if brand: hard_constraints.append("brand")
        if color: hard_constraints.append("color")
        if size: hard_constraints.append("size")
        if material: hard_constraints.append("material")
        if gender: hard_constraints.append("gender")
        for f in features: hard_constraints.append(f"feature_{f}")

        optional_constraints = []
        if use_case: optional_constraints.append("use_case")

        raw_intent = {
            "product_type": product_type,
            "category": category or product_type,
            "budget": {
                "max_price": max_price,
                "currency": "INR"
            },
            "attributes": {
                "brand": brand,
                "color": color,
                "gender": gender,
                "size": size,
                "material": material,
                "required_features": features
            },
            "use_case": use_case,
            "explicit_hard_constraints": hard_constraints,
            "optional_constraints": optional_constraints,
            "requested_cart_action": {
                "action": cart_action,
                "target_product_query": target_query,
                "quantity": qty
            }
        }
        return cls._normalize_structured_intent(raw_intent, user_text)

    @classmethod
    def _normalize_structured_intent(cls, intent_data: Dict[str, Any], raw_query: str) -> Dict[str, Any]:
        """
        Normalizes structured intent dictionary into the internal agent representation.
        """
        attrs = intent_data.get("attributes", {})
        budget = intent_data.get("budget", {})
        max_p = budget.get("max_price") if isinstance(budget, dict) else intent_data.get("max_price")

        prod_type = intent_data.get("product_type")
        cat = intent_data.get("category") or prod_type

        cart_action_data = intent_data.get("requested_cart_action", {})

        return {
            "query": raw_query,
            "category": cat,
            "head_noun": prod_type or cat,
            "max_price": max_p,
            "brand": attrs.get("brand"),
            "color": attrs.get("color"),
            "gender": attrs.get("gender"),
            "size": attrs.get("size"),
            "material": attrs.get("material"),
            "required_features": attrs.get("required_features", []),
            "use_case": intent_data.get("use_case"),
            "explicit_hard_constraints": intent_data.get("explicit_hard_constraints", []),
            "optional_constraints": intent_data.get("optional_constraints", []),
            "cart_action": cart_action_data.get("action", "NONE"),
            "cart_target_query": cart_action_data.get("target_product_query"),
            "structured_intent": intent_data
        }

commerce_intent_resolver = CommerceIntentResolver()
