import re
from typing import Dict, Any, List, Optional
from app.agent.tools import search_catalog

class CartIntentDetector:
    """
    Cart Action Intelligence Module for RazorFlow AI.
    Detects cart action (ADD, REMOVE, UPDATE, VIEW, NONE),
    matches target product in cart or catalog, and extracts requested quantity.
    """

    REMOVE_KEYWORDS = [
        "remove", "delete", "take out", "take it out", "get rid of",
        "drop", "discard", "clear item", "remove from cart", "take off",
        "take out of cart", "delete from cart"
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
            return {"action": "NONE", "target_item": None, "quantity": 1}

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
            return {"action": "VIEW", "target_item": None, "quantity": 1}

        # 3. Target Product Identification
        target_item = cls._find_target_product(text, current_cart, action)

        return {
            "action": action,
            "target_item": target_item,
            "quantity": requested_qty
        }

    @classmethod
    def _find_target_product(cls, text: str, current_cart: List[Dict[str, Any]], action: str) -> Optional[Dict[str, Any]]:
        # Product Category Tokens
        category_tokens = ["laptop bag", "laptop sleeve", "bag", "sleeve", "mouse", "headphone", "headphones", "laptop", "monitor", "keyboard", "hub", "cooler"]

        if action in ["REMOVE", "UPDATE"]:
            # Match strictly against existing items in cart
            for item in current_cart:
                p_name = item.get("name", "").lower()
                p_id = item.get("product_id", "").lower()
                
                if p_id in text or ("bag" in text and ("bag" in p_name or "sleeve" in p_name)) or ("sleeve" in text and "sleeve" in p_name) or ("mouse" in text and "mouse" in p_name) or ("laptop" in text and "laptop" in p_name and "bag" not in text and "sleeve" not in text) or ("headphone" in text and "headphone" in p_name):
                    return item

                words = [w for w in p_name.split() if len(w) > 3]
                if any(w in text for w in words):
                    return item

            # If user explicitly requested a category token (e.g. "headphones") that is NOT in cart, return None!
            if any(tok in text for tok in category_tokens):
                return None

            # If cart has items and relative position reference used
            if current_cart:
                if "first" in text or "1st" in text:
                    return current_cart[0]
                elif "second" in text or "2nd" in text and len(current_cart) > 1:
                    return current_cart[1]
                elif len(current_cart) == 1:
                    return current_cart[0]

            return None

        # For ADD action:
        if action == "ADD":
            category = None
            clean_query = text
            if "bag" in text or "sleeve" in text:
                category = "Accessories"
                clean_query = "bag sleeve"
            elif "mouse" in text:
                category = "Accessories"
                clean_query = "mouse"
            elif "keyboard" in text:
                category = "Accessories"
                clean_query = "keyboard"
            elif "hub" in text:
                category = "Accessories"
                clean_query = "hub"
            elif "laptop" in text or "notebook" in text or "macbook" in text:
                category = "Laptops"
                clean_query = "laptop"
            elif "headphone" in text or "audio" in text:
                category = "Audio"
                clean_query = "headphones"

            candidates = search_catalog(query=clean_query, category=category)
            if not candidates and category:
                candidates = search_catalog(category=category)
            if not candidates:
                candidates = search_catalog()

            if "second" in text or "2nd" in text or "number 2" in text:
                if len(candidates) >= 2:
                    return candidates[1]
            elif "first" in text or "1st" in text or "recommended" in text or "top" in text:
                if candidates:
                    return candidates[0]
            
            for p in candidates:
                p_name = p.get("name", "").lower()
                if ("bag" in text or "sleeve" in text) and ("bag" in p_name or "sleeve" in p_name):
                    return p
                if "mouse" in text and "mouse" in p_name:
                    return p
                if "laptop" in text and "bag" not in text and "sleeve" not in text and "laptop" in p_name:
                    return p

            if candidates:
                return candidates[0]

        return None
