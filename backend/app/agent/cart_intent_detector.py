import re
from typing import Dict, Any, List, Optional
from app.agent.tools import search_catalog

class CartIntentDetector:
    """
    Cart Action Intelligence Module for RazorFlow AI.
    Detects cart action (ADD, REMOVE, UPDATE, VIEW, NONE),
    matches target product in cart or catalog, and extracts requested quantity.
    Grounded in strict cart action safety.
    """

    REMOVE_KEYWORDS = [
        "remove", "delete", "take out", "take it out", "get rid of",
        "drop", "discard", "clear item", "remove from cart", "take off",
        "take out of cart", "delete from cart", "don't want", "dont want"
    ]

    UPDATE_KEYWORDS = [
        "update", "change quantity", "change count", "increase to", "decrease to",
        "set quantity", "set count", "change to", "make it"
    ]

    VIEW_KEYWORDS = [
        "view cart", "show cart", "what's in my cart", "whats in my cart",
        "check cart", "see cart", "display cart", "cart contents",
        "show my items", "show cart items", "view my cart", "show my cart",
        "my cart", "open cart"
    ]

    ADD_KEYWORDS = [
        "add", "put in", "put it in", "insert", "include", "put inside",
        "add to cart", "add this", "add recommended", "place in cart",
        "add to my cart", "buy and add"
    ]

    @classmethod
    def detect_intent(cls, message: str, current_cart: List[Dict[str, Any]]) -> Dict[str, Any]:
        text = message.lower().strip()

        # 1. Action Identification (Priority: REMOVE -> UPDATE -> VIEW -> ADD)
        action = "NONE"
        if any(kw in text for kw in cls.REMOVE_KEYWORDS):
            action = "REMOVE"
        elif any(kw in text for kw in cls.UPDATE_KEYWORDS):
            action = "UPDATE"
        elif any(kw in text for kw in cls.VIEW_KEYWORDS) and not any(kw in text for kw in cls.ADD_KEYWORDS + cls.REMOVE_KEYWORDS):
            action = "VIEW"
        elif any(kw in text for kw in cls.ADD_KEYWORDS):
            action = "ADD"

        if action == "NONE":
            return {"action": "NONE", "target_item": None, "quantity": 1, "is_ambiguous": False}

        # 2. Extract Requested Quantity
        requested_qty = 1
        num_match = re.search(r'\b(?:to|make it|set quantity to|set count to|quantity|count)?\s*(\d+)\b', text)
        if num_match:
            try:
                val = int(num_match.group(1))
                if val > 0:
                    requested_qty = val
            except ValueError:
                requested_qty = 1
        elif "two" in text:
            requested_qty = 2
        elif "three" in text:
            requested_qty = 3

        if action == "VIEW":
            return {"action": "VIEW", "target_item": None, "quantity": 1, "is_ambiguous": False}

        # 3. Target Product Identity Resolution
        catalog = search_catalog()
        target_item, is_ambiguous = cls._resolve_target_product(text, current_cart, catalog, action)

        return {
            "action": action,
            "target_item": target_item,
            "quantity": requested_qty,
            "is_ambiguous": is_ambiguous
        }

    @classmethod
    def _resolve_target_product(cls, text: str, current_cart: List[Dict[str, Any]], catalog: List[Dict[str, Any]], action: str):
        from app.agent.catalog_registry import catalog_registry
        t = text.lower().strip()

        if action in ["REMOVE", "UPDATE"]:
            if not current_cart:
                return None, False

            # Dynamic brand / model match from CatalogRegistry in current cart
            for item in current_cart:
                p_name = item.get("name", "").lower()
                p_id = item.get("product_id", "").lower()

                for brand in catalog_registry.brands:
                    if brand in t and (brand in p_name or brand in p_id):
                        return item, False

                if p_name in t or p_id in t:
                    return item, False

                words = [w for w in re.findall(r'\b\w+\b', p_name) if len(w) >= 3 and w not in ["laptop", "edition", "wireless", "developer"]]
                if any(w in t for w in words):
                    return item, False

            # Generic item type match in cart
            if "bag" in t or "sleeve" in t:
                matches = [i for i in current_cart if "sleeve" in i.get("name", "").lower() or "bag" in i.get("name", "").lower()]
                if len(matches) == 1: return matches[0], False
            elif "mouse" in t:
                matches = [i for i in current_cart if "mouse" in i.get("name", "").lower()]
                if len(matches) == 1: return matches[0], False
            elif "laptop" in t:
                matches = [i for i in current_cart if any(b in i.get("name", "").lower() for b in catalog_registry.brands if b in ["zenbook", "thinkpad", "macbook", "legion", "asus", "apple", "lenovo"])]
                if len(matches) == 1: return matches[0], False

            # Position references
            if "first" in t or "1st" in t:
                return current_cart[0], False
            elif ("second" in t or "2nd" in t) and len(current_cart) > 1:
                return current_cart[1], False
            elif len(current_cart) == 1 and any(k in t for k in ["it", "item", "product", "this"]):
                return current_cart[0], False

            return None, False

        # For ADD action: resolve exact catalog product identity
        if action == "ADD":
            # 1. Check dynamic brand / model name in catalog
            for brand in catalog_registry.brands:
                if brand in t:
                    for p in catalog:
                        p_name = p.get("name", "").lower()
                        p_id = p.get("id", "").lower()
                        if brand in p_name or brand in p_id:
                            return p, False

            # 2. Check full product title match
            for p in catalog:
                p_name = p.get("name", "").lower()
                if p_name in t:
                    return p, False

            # 3. Check product type specific candidates
            matched_candidates = []
            if "sleeve" in t or "bag" in t:
                matched_candidates = [p for p in catalog if "sleeve" in p.get("name", "").lower() or "bag" in p.get("name", "").lower()]
            elif "mouse" in t or "mice" in t:
                matched_candidates = [p for p in catalog if "mouse" in p.get("name", "").lower()]
            elif "keyboard" in t:
                matched_candidates = [p for p in catalog if "keyboard" in p.get("name", "").lower()]
            elif "hub" in t:
                matched_candidates = [p for p in catalog if "hub" in p.get("name", "").lower()]
            elif "cooler" in t or "cooling" in t:
                matched_candidates = [p for p in catalog if "cooler" in p.get("name", "").lower() or "cooling" in p.get("name", "").lower()]
            elif "headphone" in t or "audio" in t:
                matched_candidates = [p for p in catalog if "headphone" in p.get("name", "").lower() or "acoustix" in p.get("name", "").lower()]
            elif "monitor" in t or "display" in t:
                matched_candidates = [p for p in catalog if "monitor" in p.get("name", "").lower() or "ultraview" in p.get("name", "").lower()]

            if len(matched_candidates) == 1:
                return matched_candidates[0], False
            elif len(matched_candidates) > 1:
                return None, True

            # 4. Position-based selection fallback
            if "second" in t or "2nd" in t or "option 2" in t:
                if len(catalog) >= 2: return catalog[1], False
            elif "first" in t or "1st" in t or "recommended" in t or "top match" in t:
                if catalog: return catalog[0], False

        return None, False
