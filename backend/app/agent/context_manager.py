from typing import Dict, Any, Optional

class ContextManager:
    """
    Conversational Context Persistence Engine for RazorFlow AI.
    Accumulates user constraints (category, budget, attributes) across multi-turn user queries,
    and intelligently resets or updates context when the user switches product categories.
    """

    @classmethod
    def merge_context(cls, previous_context: Optional[Dict[str, Any]], current_intent: Dict[str, Any]) -> Dict[str, Any]:
        if not previous_context:
            previous_context = {
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
                "required_features": []
            }

        merged = previous_context.copy()

        curr_cat = current_intent.get("category")
        curr_head = current_intent.get("head_noun")
        prev_cat = previous_context.get("category")

        # Detect category switch
        category_changed = False
        if curr_cat and prev_cat:
            curr_c_clean = str(curr_cat).lower().strip()
            prev_c_clean = str(prev_cat).lower().strip()
            if curr_c_clean != prev_c_clean and not (curr_c_clean in prev_c_clean or prev_c_clean in curr_c_clean):
                category_changed = True

        if category_changed:
            # User switched product category (e.g. from laptops to headphones):
            # Reset category-specific attributes and keep new category
            merged = {
                "category": curr_cat,
                "head_noun": curr_head or curr_cat,
                "max_price": current_intent.get("max_price"),
                "brand": current_intent.get("brand"),
                "color": current_intent.get("color"),
                "gender": current_intent.get("gender"),
                "size": current_intent.get("size"),
                "material": current_intent.get("material"),
                "style": current_intent.get("style"),
                "use_case": current_intent.get("use_case"),
                "required_features": current_intent.get("required_features", [])[:]
            }
        else:
            # Merge/accumulate constraints
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
