import re
from typing import Dict, Any, Optional

class ContextManager:
    """
    Conversational Context Persistence Engine for RazorFlow AI.
    Accumulates user constraints (category, budget, attributes) ONLY for explicit follow-up queries.
    Strictly isolates new product requests from previous context.
    """

    @classmethod
    def is_followup_query(cls, user_message: str, previous_context: Optional[Dict[str, Any]]) -> bool:
        if not previous_context or not previous_context.get("category"):
            return False

        t = user_message.lower().strip()

        # Follow-up indicators: constraint refinement, demonstrative pronouns, attribute preferences, or follow-up actions
        followup_keywords = [
            "cheaper", "expensive", "under ", "below ", "less than", "within ", "budget",
            "in red", "in blue", "in black", "in white", "in silver", "in gold", "in pink",
            "with ", "size ", "brand ", "show more", "next", "alternative", "other options",
            "another option", "best rated", "highest rated", "recommendation",
            "this", "that", "these", "those", "it", "one", "first", "second", "third",
            "former", "latter", "add this", "buy it", "compare", "versus", " vs ", "which one",
            "tell me more", "what about", "how about", "battery", "life", "focus", "care", "mostly",
            "prefer", "prioritize"
        ]

        return any(re.search(r'\b' + re.escape(kw.strip()) + r'\b', t) if len(kw.strip()) > 2 else kw in t for kw in followup_keywords)

    @classmethod
    def merge_context(cls, previous_context: Optional[Dict[str, Any]], current_intent: Dict[str, Any]) -> Dict[str, Any]:
        curr_cat = current_intent.get("category")
        curr_head = current_intent.get("head_noun")
        user_query = current_intent.get("query", "")

        # Default empty context template
        empty_context = {
            "category": None,
            "head_noun": None,
            "max_price": None,
            "brand": None,
            "color": None,
            "gender": None,
            "size": None,
            "material": None,
            "style": None,
            "use_case": None,
            "focus_area": "general",
            "required_features": []
        }

        # If no previous context exists, return current intent's context
        if not previous_context:
            merged = empty_context.copy()
            for key in merged.keys():
                if key in current_intent and current_intent[key] is not None:
                    merged[key] = current_intent[key]
            merged["category"] = curr_cat
            merged["head_noun"] = curr_head or curr_cat
            return merged

        prev_cat = previous_context.get("category")
        is_followup = cls.is_followup_query(user_query, previous_context)

        # Detect explicit category change
        category_changed = False
        if curr_cat and prev_cat:
            curr_c_clean = str(curr_cat).lower().strip()
            prev_c_clean = str(prev_cat).lower().strip()
            if curr_c_clean != prev_c_clean and not (curr_c_clean in prev_c_clean or prev_c_clean in curr_c_clean):
                category_changed = True

        # Rule: A new query or explicit category change MUST start fresh and NOT inherit previous context
        if category_changed or (curr_cat and not is_followup) or (not is_followup and curr_cat != prev_cat):
            merged = empty_context.copy()
            for key in merged.keys():
                if key in current_intent and current_intent[key] is not None:
                    merged[key] = current_intent[key]
            merged["category"] = curr_cat
            merged["head_noun"] = curr_head or curr_cat
            return merged

        # If it IS a valid follow-up query, preserve previous context and merge new constraints
        merged = previous_context.copy()

        if curr_cat:
            merged["category"] = curr_cat
            merged["head_noun"] = curr_head or curr_cat

        if current_intent.get("max_price") is not None:
            merged["max_price"] = current_intent["max_price"]

        if current_intent.get("brand"):
            merged["brand"] = current_intent["brand"]

        if current_intent.get("color"):
            merged["color"] = current_intent["color"]

        if current_intent.get("gender"):
            merged["gender"] = current_intent["gender"]

        if current_intent.get("size"):
            merged["size"] = current_intent["size"]

        if current_intent.get("material"):
            merged["material"] = current_intent["material"]

        if current_intent.get("style"):
            merged["style"] = current_intent["style"]

        if current_intent.get("use_case"):
            merged["use_case"] = current_intent["use_case"]

        curr_feats = current_intent.get("required_features", [])
        prev_feats = merged.get("required_features", [])
        for f in curr_feats:
            if f not in prev_feats:
                prev_feats.append(f)
        merged["required_features"] = prev_feats

        return merged

context_manager = ContextManager()
