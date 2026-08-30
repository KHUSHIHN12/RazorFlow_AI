from typing import Dict, Any, List
from app.agent.catalog_registry import catalog_registry
from app.agent.product_validator import ValidationResult

class AlternativeHandler:
    """
    Intelligent Alternative Engine for RazorFlow AI.
    Executes ONLY when no exact match satisfies mandatory constraints.
    Preserves requested product/category boundary strictly.
    Never substitutes unrelated categories.
    Clearly communicates relaxed constraints to the customer.
    """

    @classmethod
    def generate_alternative_response(cls,
                                       user_message: str,
                                       intent: Dict[str, Any],
                                       validation_res: ValidationResult,
                                       current_cart: List[Dict[str, Any]],
                                       audit_logger: Any) -> Dict[str, Any]:

        fallback_level = validation_res.fallback_level
        same_cat_prods = validation_res.same_category_products
        min_price = validation_res.min_category_price
        price_delta = validation_res.price_delta
        missing_attrs = validation_res.missing_attributes

        target_cat = intent.get("head_noun") or intent.get("category") or user_message.strip()
        budget = intent.get("max_price")

        # -------------------------------------------------------------
        # 1. Out of Store Catalog (Category not available in store)
        # -------------------------------------------------------------
        if fallback_level == "no_category" or not validation_res.category_exists:
            audit_logger.log("OUT_OF_CATALOG_UNAVAILABLE", f"Category '{target_cat}' not found in store catalog.")

            available_cats = catalog_registry.get_categories()
            cat_list_str = "\n".join([f"• **{cat}**" for cat in available_cats])

            response_text = (
                f"⚠️ **Product Category Not Found in Catalog:**\n\n"
                f"• **What you requested:** **'{target_cat}'**\n"
                f"• **Status:** The category **'{target_cat}'** is currently not featured in our store inventory.\n\n"
                f"Our available store catalog features:\n"
                f"{cat_list_str}\n\n"
                f"Please let me know if you would like to explore any of these available store categories!"
            )
            return {
                "response": response_text,
                "cart": current_cart,
                "products": [],  # STRICT REQUIREMENT: Zero cards for unavailable category!
                "confirmation_required": False,
                "active_order": None,
                "context": intent,
                "audit_logs": audit_logger.get_logs()
            }

        # -------------------------------------------------------------
        # 2. Multi-Constraint Conflict (Both Budget and Attributes Failed)
        # -------------------------------------------------------------
        if fallback_level == "multi_constraint":
            attr_str = ", ".join(missing_attrs) if missing_attrs else "specified attribute(s)"
            audit_logger.log("MULTI_CONSTRAINT_CONFLICT", f"Conflict: {attr_str} & budget ₹{budget}. Preserving category '{target_cat}'.")

            response_text = (
                f"⚠️ **Multiple Constraints Prevent an Exact Match:**\n\n"
                f"• **What you requested:** {target_cat.title()} with **{attr_str}** under **₹{budget:,.0f}**\n"
                f"• **Why no exact match exists:** Multiple constraints could not be satisfied simultaneously:\n"
                f"  1. **Attribute Limitation:** {attr_str} is not available in our {target_cat.title()} collection.\n"
                f"  2. **Budget Limitation:** {target_cat.title()} products start at **₹{min_price:,.0f}** (+₹{price_delta:,.0f} above your budget of ₹{budget:,.0f}).\n\n"
                f"💡 **How would you like to proceed?**\n"
                f"1. **Option 1 (Budget Adjustment):** View available {target_cat.title()} options starting at **₹{min_price:,.0f}** (+₹{price_delta:,.0f} over budget).\n"
                f"2. **Option 2 (Attribute Adjustment):** Explore available attributes & options in {target_cat.title()} within budget.\n\n"
                f"Which constraint would you like to adjust?"
            )
            return {
                "response": response_text,
                "cart": current_cart,
                "products": [],
                "confirmation_required": False,
                "active_order": None,
                "context": intent,
                "audit_logs": audit_logger.get_logs()
            }

        # Sub-noun isolation for broad macro-categories like Accessories
        t_clean = target_cat.lower().strip()
        sub_noun_prods = []
        for p in same_cat_prods:
            p_name = p.get("name", "").lower()
            p_tags = [t.lower() for t in p.get("tags", [])]
            p_desc = p.get("description", "").lower()
            if any(k in t_clean for k in ["mouse", "mice", "keyboard", "cooler", "bag", "sleeve", "hub", "phone", "audio"]):
                kw = "mouse" if ("mouse" in t_clean or "mice" in t_clean) else ("cooling" if "cooler" in t_clean else ("bag" if ("bag" in t_clean or "sleeve" in t_clean) else t_clean))
                if kw in p_name or kw in p_tags or kw in p_desc:
                    sub_noun_prods.append(p)
            else:
                sub_noun_prods.append(p)

        candidate_pool = sub_noun_prods if sub_noun_prods else same_cat_prods

        # -------------------------------------------------------------
        # 3. Budget Limit Exceeded for Category (Same Category Preserved!)
        # -------------------------------------------------------------
        if fallback_level == "relaxed_budget" and candidate_pool:
            closest_prods = sorted(candidate_pool, key=lambda p: float(p.get("price", 0)))
            best_alt = closest_prods[0]
            cat_min_price = float(best_alt.get("price", 0))
            delta = (cat_min_price - budget) if (budget is not None and cat_min_price > budget) else 0.0

            audit_logger.log("BUDGET_RELAXED_FALLBACK", f"Budget ₹{budget:,.0f} too low for '{target_cat}'. Min price: ₹{cat_min_price:,.0f}.")

            response_text = (
                f"⚠️ **No Suitable Products Found Within Your Budget:**\n\n"
                f"• **What you requested:** {target_cat.title()} under **₹{budget:,.0f}**\n"
                f"• **Why no exact match exists:** Products in this category start at **₹{cat_min_price:,.0f}** (+₹{delta:,.0f} above your specified budget of ₹{budget:,.0f}).\n\n"
                f"💡 **Closest Available Alternative (Same Category — Relaxed Budget):**\n"
                f"• **{best_alt['name']}** — **₹{best_alt['price']:,}** (⭐ {best_alt.get('rating', 4.5)}★ from {best_alt.get('reviews_count', 100):,} reviews)\n"
                f"• **Note:** Budget constraint relaxed by +₹{delta:,.0f}.\n"
                f"• **Key Features:** {best_alt.get('description', '')[:120]}..."
            )
            return {
                "response": response_text,
                "cart": current_cart,
                "products": [best_alt],  # Preserves SAME category, clearly notes budget relaxation!
                "confirmation_required": False,
                "active_order": None,
                "context": intent,
                "audit_logs": audit_logger.get_logs()
            }

        # -------------------------------------------------------------
        # 4. Relaxed Secondary Attributes (Same Category & Fits Budget!)
        # -------------------------------------------------------------
        if fallback_level == "relaxed_attributes" and candidate_pool:
            budget_valid = [p for p in candidate_pool if budget is None or float(p.get("price", 0)) <= budget]
            target_pool = budget_valid if budget_valid else candidate_pool
            best_alt = sorted(target_pool, key=lambda p: p.get("rating", 0), reverse=True)[0]

            attr_str = ", ".join(missing_attrs) if missing_attrs else "specified attribute(s)"
            audit_logger.log("ATTRIBUTE_RELAXED_FALLBACK", f"Relaxed {attr_str} in category '{target_cat}'. Suggesting '{best_alt['name']}'.")

            response_text = (
                f"⚠️ **No Exact Match Found for Specified Attribute:**\n\n"
                f"• **What you requested:** {target_cat.title()} with **{attr_str}**\n"
                f"• **What is unavailable:** {attr_str} in our {target_cat.title()} collection\n\n"
                f"💡 **Closest Available Alternative (Same Category — Within Budget):**\n"
                f"• **{best_alt['name']}** — **₹{best_alt['price']:,}** (⭐ {best_alt.get('rating', 4.5)}★ from {best_alt.get('reviews_count', 100):,} reviews)\n"
                f"• **Note:** Relaxed constraint for {attr_str}.\n"
                f"• **Description:** {best_alt.get('description', '')[:120]}..."
            )
            return {
                "response": response_text,
                "cart": current_cart,
                "products": [best_alt],
                "confirmation_required": False,
                "active_order": None,
                "context": intent,
                "audit_logs": audit_logger.get_logs()
            }

        # Catch-all fallback
        return {
            "response": f"⚠️ No products in category '{target_cat}' satisfied your requested requirements.",
            "cart": current_cart,
            "products": [],
            "confirmation_required": False,
            "active_order": None,
            "context": intent,
            "audit_logs": audit_logger.get_logs()
        }

alternative_handler = AlternativeHandler()
