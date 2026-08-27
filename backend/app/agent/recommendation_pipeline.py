import re
from typing import Dict, Any, List, Optional
from app.agent.catalog_registry import catalog_registry
from app.agent.product_validator import product_validator, ValidationResult
from app.agent.alternative_handler import alternative_handler
from app.agent.ranking_engine import ranking_engine
from app.agent.context_manager import context_manager
from app.agent.cart_intent_detector import CartIntentDetector
from app.agent.bundle_engine import bundle_engine
from app.agent.audit_logger import audit_logger
from app.services.analytics_service import analytics_service
from app.agent.tools import search_catalog, manage_cart, create_razorpay_order

class StructuredRequirements:
    """
    Unified Container for Customer Intent, Constraints, and Context.
    """
    def __init__(self,
                 category: Optional[str] = None,
                 head_noun: Optional[str] = None,
                 max_price: Optional[float] = None,
                 brand: Optional[str] = None,
                 color: Optional[str] = None,
                 gender: Optional[str] = None,
                 size: Optional[str] = None,
                 material: Optional[str] = None,
                 style: Optional[str] = None,
                 use_case: Optional[str] = None,
                 focus_area: str = "general",
                 required_features: List[str] = None,
                 intent_type: str = "product_search",
                 raw_query: str = ""):
        self.category = category
        self.head_noun = head_noun or category
        self.max_price = max_price
        self.brand = brand
        self.color = color
        self.gender = gender
        self.size = size
        self.material = material
        self.style = style
        self.use_case = use_case
        self.focus_area = focus_area
        self.required_features = required_features or []
        self.intent_type = intent_type
        self.raw_query = raw_query

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "head_noun": self.head_noun,
            "max_price": self.max_price,
            "brand": self.brand,
            "color": self.color,
            "gender": self.gender,
            "size": self.size,
            "material": self.material,
            "style": self.style,
            "use_case": self.use_case,
            "focus_area": self.focus_area,
            "required_features": self.required_features,
            "intent_type": self.intent_type,
            "query": self.raw_query
        }

class RecommendationPipeline:
    """
    Single Authoritative Recommendation & Commerce Pipeline.
    
    Flow:
    User Intent → Structured Requirements → Context Merge → Product Resolution → Validation → Ranking → Alternative Handling → Response
    
    Guarantees:
    - Validation before ranking.
    - Only validated products reach response.
    - Preserves category boundary strictly.
    - Single point of truth for cart actions and recommendations.
    """

    @classmethod
    def execute(cls,
                user_message: str,
                current_cart: List[Dict[str, Any]],
                confirmed_pay: bool = False,
                session_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

        audit_logger.clear()
        analytics_service.log_intent(user_message)
        audit_logger.log("INTENT_RECEIVED", f"Customer message: '{user_message}'")

        user_text = user_message.lower().strip()
        updated_cart = [item.copy() for item in current_cart]

        # -------------------------------------------------------------
        # STEP 1 & 2: Dedicated Commerce Intent Resolution Layer (LLM / Structured Intent)
        # -------------------------------------------------------------
        from app.agent.intent_resolver import commerce_intent_resolver
        from app.services.ai_service import ai_service
        
        parsed_intent = commerce_intent_resolver.resolve_intent(
            user_message=user_message,
            use_llm=ai_service.use_llm,
            api_key=ai_service.api_key
        )
        
        reqs = StructuredRequirements(
            category=parsed_intent.get("category"),
            head_noun=parsed_intent.get("head_noun"),
            max_price=parsed_intent.get("max_price"),
            brand=parsed_intent.get("brand"),
            color=parsed_intent.get("color"),
            gender=parsed_intent.get("gender"),
            size=parsed_intent.get("size"),
            material=parsed_intent.get("material"),
            style=parsed_intent.get("style"),
            use_case=parsed_intent.get("use_case"),
            focus_area=parsed_intent.get("focus_area", "general"),
            required_features=parsed_intent.get("required_features", []),
            intent_type=parsed_intent.get("structured_intent", {}).get("intent_type", "product_search"),
            raw_query=user_message
        )

        # -------------------------------------------------------------
        # STEP 3: Conversational Context Merge
        # -------------------------------------------------------------
        merged_context = context_manager.merge_context(session_context, reqs.to_dict())

        attr_log_parts = []
        if merged_context.get("category"): attr_log_parts.append(f"category = \"{merged_context['category']}\"")
        if merged_context.get("color"): attr_log_parts.append(f"color = \"{merged_context['color']}\"")
        if merged_context.get("gender"): attr_log_parts.append(f"gender = \"{merged_context['gender']}\"")
        if merged_context.get("size"): attr_log_parts.append(f"size = \"{merged_context['size']}\"")
        if merged_context.get("brand"): attr_log_parts.append(f"brand = \"{merged_context['brand']}\"")
        if merged_context.get("max_price"): attr_log_parts.append(f"budget = {merged_context['max_price']}")
        extracted_summary = ", ".join(attr_log_parts) if attr_log_parts else "unconstrained query"
        audit_logger.log("EXTRACTED_INTENT", f"Active Intent: {extracted_summary}")

        # -------------------------------------------------------------
        # STEP 4: Specialized Intent Routing (Cart Actions, Payment, Comparison, Bundles)
        # -------------------------------------------------------------

        # A. Cart Selection Command ("buy only the laptop", "buy the mouse"...)
        if any(k in user_text for k in ["buy only", "buy the", "only buy", "checkout only"]):
            audit_logger.log("CART_SELECTION_COMMAND", "Parsing specific cart item selection query.")
            matched_items = []
            for item in updated_cart:
                item_name_lower = item["name"].lower()
                if any(kw in user_text for kw in item_name_lower.split() if len(kw) > 3) or ("laptop" in user_text and "lap" in item.get("product_id", "")):
                    item["selected"] = True
                    matched_items.append(item)
                else:
                    item["selected"] = False

            if matched_items:
                selected_inr = sum(i["price"] * i["quantity"] for i in matched_items)
                selected_paise = sum(i["price_paise"] * i["quantity"] for i in matched_items)
                item_names = ", ".join([f"{i['name']} (₹{i['price']:,})" for i in matched_items])
                
                response_text = (
                    f"🛒 **Checkout Selection Prepared:**\n\n"
                    f"Selected item(s): **{item_names}**\n"
                    f"Selected Order Total: **₹{selected_inr:,}** ({selected_paise} paise)\n\n"
                    f"*(Note: Unselected items remain safely in your cart.)*\n\n"
                    f"Would you like me to proceed to generate the authentic Razorpay Checkout Order?"
                )
                return {
                    "response": response_text,
                    "cart": updated_cart,
                    "products": [],
                    "confirmation_required": True,
                    "active_order": None,
                    "context": merged_context,
                    "audit_logs": audit_logger.get_logs()
                }

        # B. Cross-Sell Query
        if any(k in user_text for k in ["what else", "cross sell", "accessory", "complementary", "should i buy with", "what accessories"]):
            audit_logger.log("CROSS_SELL_QUERY", "Analyzing cart for complementary accessories.")
            accs = search_catalog(category="Accessories")
            cs = accs[0] if accs else search_catalog()[0]
            response_text = (
                f"💡 **Contextual Cross-Sell Recommendation:**\n\n"
                f"Based on your current setup, we recommend adding **{cs['name']}** (₹{cs['price']:,}).\n"
                f"• **Why it's useful:** {cs['description']}\n"
                f"• **Customer Rating:** ⭐ {cs['rating']} from {cs['reviews_count']:,} reviews."
            )
            return {
                "response": response_text,
                "cart": updated_cart,
                "products": [cs],
                "confirmation_required": False,
                "active_order": None,
                "context": merged_context,
                "audit_logs": audit_logger.get_logs()
            }

        # C. Payment Guardrail Check
        selected_items = [i for i in updated_cart if i.get("selected") is True]
        selected_inr = sum(i["price"] * i["quantity"] for i in selected_items)
        selected_paise = sum(i["price_paise"] * i["quantity"] for i in selected_items)

        is_pay_intent = any(k in user_text for k in ["buy", "checkout", "pay", "order", "purchase", "proceed"])
        is_explicit_confirm = confirmed_pay or any(k in user_text for k in ["yes", "confirm", "proceed to pay", "approve", "lets do it", "let's pay", "proceed with order"])

        if (is_pay_intent or is_explicit_confirm) and len(selected_items) == 0:
            audit_logger.log("CHECKOUT_FAILED", "No items selected in Buying List for checkout.")
            return {
                "response": "⚠️ **No items selected for checkout.**\n\nYour buying list is currently empty. Please select at least one item from your cart to proceed with checkout.",
                "cart": updated_cart,
                "products": [],
                "confirmation_required": False,
                "active_order": None,
                "context": merged_context,
                "audit_logs": audit_logger.get_logs()
            }

        if is_explicit_confirm and len(selected_items) > 0:
            audit_logger.log("GUARDRAIL_PASSED", f"User explicitly confirmed payment for {len(selected_items)} selected item(s). Calling create_razorpay_order.")
            order_res = create_razorpay_order(amount_paise=selected_paise, currency="INR")
            active_order = {
                "order_id": order_res["order_id"],
                "is_authentic_order": order_res.get("is_authentic_order", False),
                "amount_paise": selected_paise,
                "amount_inr": selected_inr,
                "currency": "INR",
                "key_id": order_res.get("key_id", ""),
                "items": selected_items
            }
            return {
                "response": f"✅ **Razorpay Order Generated!**\n\nOrder ID: `{order_res['order_id']}`\nSelected Items: **{len(selected_items)} item(s)**\nTotal Selected Amount: **₹{selected_inr:,}** ({selected_paise} paise)\n\nClick the button below to launch the secure **Razorpay Checkout Modal**.",
                "cart": updated_cart,
                "products": [],
                "confirmation_required": False,
                "active_order": active_order,
                "context": merged_context,
                "audit_logs": audit_logger.get_logs()
            }
        elif is_pay_intent and len(selected_items) > 0:
            audit_logger.log("GUARDRAIL_TRIGGERED", "Financial action requested. Prompting for explicit user confirmation.")
            item_names = ", ".join([f"{i['name']}" for i in selected_items])
            return {
                "response": f"⚠️ **Payment Confirmation Required (Deterministic Guardrail)**\n\nYou have selected **{len(selected_items)} item(s)** ({item_names}) for checkout totaling **₹{selected_inr:,}**.\n\nWould you like me to proceed to generate the authentic Razorpay Checkout Order?",
                "cart": updated_cart,
                "products": [],
                "confirmation_required": True,
                "active_order": None,
                "context": merged_context,
                "audit_logs": audit_logger.get_logs()
            }

        # D. Goal-Based Shopping Bundle Request
        if any(k in user_text for k in ["setup", "bundle", "complete package", "complete programming setup", "student setup"]):
            audit_logger.log("GOAL_ENGINE_TRIGGERED", "Constructing multi-product setup bundle.")
            budget_val = merged_context.get("max_price") or 70000.0
            bundle_res = bundle_engine.create_goal_bundle(user_message, total_budget=budget_val)
            return {
                "response": bundle_res["explanation"],
                "cart": updated_cart,
                "products": bundle_res["items"],
                "bundle_data": bundle_res,
                "confirmation_required": False,
                "active_order": None,
                "context": merged_context,
                "audit_logs": audit_logger.get_logs()
            }

        # E. Product Comparison Request
        if any(k in user_text for k in ["compare", "versus", " vs ", "difference"]):
            audit_logger.log("COMPARISON_ENGINE_TRIGGERED", "Executing side-by-side product comparison.")
            cat_query = merged_context.get("category") or "Laptops"
            laptops = search_catalog(category=cat_query) if cat_query in catalog_registry.get_categories() else search_catalog(category="Laptops")
            ranked_laptops = ranking_engine.rank_catalog(laptops, query=user_message)
            top_two = [r["product"] for r in ranked_laptops[:2]]
            if len(top_two) >= 2:
                p1, p2 = top_two[0], top_two[1]
                response_text = (
                    f"⚖️ **Side-by-Side Product Comparison:**\n\n"
                    f"1. **{p1['name']}** — **₹{p1['price']:,}** (⭐ {p1['rating']} | {p1['reviews_count']:,} reviews)\n"
                    f"   • Processor: {p1['specs'].get('processor', 'N/A')}\n"
                    f"   • RAM: {p1['specs'].get('ram', 'N/A')}\n"
                    f"   • Storage: {p1['specs'].get('storage', 'N/A')}\n\n"
                    f"2. **{p2['name']}** — **₹{p2['price']:,}** (⭐ {p2['rating']} | {p2['reviews_count']:,} reviews)\n"
                    f"   • Processor: {p2['specs'].get('processor', 'N/A')}\n"
                    f"   • RAM: {p2['specs'].get('ram', 'N/A')}\n"
                    f"   • Storage: {p2['specs'].get('storage', 'N/A')}\n\n"
                    f"💡 **Recommendation:** Choose **{p1['name']}** if you prioritize performance & battery life, or **{p2['name']}** for maximum budget savings."
                )
                return {
                    "response": response_text,
                    "cart": updated_cart,
                    "products": top_two,
                    "confirmation_required": False,
                    "active_order": None,
                    "context": merged_context,
                    "audit_logs": audit_logger.get_logs()
                }

        # F. Cart Actions (ADD, REMOVE, UPDATE, VIEW)
        cart_intent = CartIntentDetector.detect_intent(user_message, updated_cart)
        action_type = cart_intent["action"]

        if action_type != "NONE":
            audit_logger.log("CART_ACTION_INTELLIGENCE", f"Detected cart action '{action_type}' for query '{user_message}'")
            target_item = cart_intent["target_item"]
            req_qty = cart_intent["quantity"]

            if action_type == "VIEW":
                if not updated_cart:
                    response_text = "🛒 **Your cart is currently empty.**"
                else:
                    item_lines = "\n".join([f"• **{i['name']}** — {i['quantity']}x ₹{i['price']:,} = ₹{i['price']*i['quantity']:,}" for i in updated_cart])
                    total_val = sum(i["price"] * i["quantity"] for i in updated_cart)
                    response_text = f"🛒 **Your Shopping Cart:**\n\n{item_lines}\n\n**Total:** ₹{total_val:,} ({len(updated_cart)} item types)"
                return {
                    "response": response_text,
                    "cart": updated_cart,
                    "products": [],
                    "confirmation_required": False,
                    "active_order": None,
                    "context": merged_context,
                    "audit_logs": audit_logger.get_logs()
                }

            elif action_type == "REMOVE":
                if not target_item:
                    response_text = "⚠️ Could not find the requested item in your shopping cart. No items were removed."
                else:
                    res = manage_cart(updated_cart, action="remove", product_id=target_item["product_id"])
                    updated_cart = res["cart"]
                    audit_logger.log("CART_MUTATED", f"Removed '{target_item['name']}' from cart.")
                    response_text = f"🗑️ Removed **{target_item['name']}** from your cart.\nCurrent Cart Total: **₹{res['total_inr']:,}** ({res['item_count']} items)."
                return {
                    "response": response_text,
                    "cart": updated_cart,
                    "products": [],
                    "confirmation_required": False,
                    "active_order": None,
                    "context": merged_context,
                    "audit_logs": audit_logger.get_logs()
                }

            elif action_type == "UPDATE":
                if not target_item:
                    response_text = "⚠️ Could not find the requested item to update in your cart."
                else:
                    res = manage_cart(updated_cart, action="update", product_id=target_item["product_id"], quantity=req_qty)
                    updated_cart = res["cart"]
                    audit_logger.log("CART_MUTATED", f"Updated '{target_item['name']}' quantity to {req_qty}.")
                    response_text = f"✏️ Updated **{target_item['name']}** quantity to **{req_qty}**.\nCurrent Cart Total: **₹{res['total_inr']:,}** ({res['item_count']} items)."
                return {
                    "response": response_text,
                    "cart": updated_cart,
                    "products": [],
                    "confirmation_required": False,
                    "active_order": None,
                    "context": merged_context,
                    "audit_logs": audit_logger.get_logs()
                }

            elif action_type == "ADD":
                is_ambiguous = cart_intent.get("is_ambiguous", False)
                matched_prod = target_item
                if is_ambiguous or not matched_prod:
                    audit_logger.log("AMBIGUOUS_PRODUCT_RESOLUTION", "Ambiguous product request for ADD action. Requesting clarification.")
                    return {
                        "response": "⚠️ **Product Identity Clarification Required:**\n\nMultiple products match your query in our store catalog. Please specify the exact product model or title you would like to add to your cart.",
                        "cart": updated_cart,
                        "products": [],
                        "confirmation_required": False,
                        "active_order": None,
                        "context": merged_context,
                        "audit_logs": audit_logger.get_logs()
                    }

                prod_id = matched_prod.get("product_id") or matched_prod.get("id")
                prod_name = matched_prod.get("name")
                prod_price = matched_prod.get("price", 0)

                res = manage_cart(updated_cart, action="add", product_id=prod_id, quantity=req_qty)
                updated_cart = res["cart"]
                audit_logger.log("CART_MUTATED", f"Added '{prod_name}' to cart. Total items: {res['item_count']}")

                response_text = f"🛒 Added **{prod_name}** (₹{prod_price:,}) to your cart!\nCurrent Cart Total: **₹{res['total_inr']:,}** ({res['item_count']} items)."
                return {
                    "response": response_text,
                    "cart": updated_cart,
                    "products": [matched_prod],
                    "confirmation_required": False,
                    "active_order": None,
                    "context": merged_context,
                    "audit_logs": audit_logger.get_logs()
                }

        # -------------------------------------------------------------
        # STEP 5: Product Validation (Validation before Ranking)
        # -------------------------------------------------------------
        audit_logger.log("PIPELINE_STAGE", "Executing: Category Filter → Attribute Filter → Budget Filter → Ranking")
        all_catalog_items = catalog_registry.get_all_products()
        validation_res = product_validator.validate_catalog(all_catalog_items, merged_context)

        # -------------------------------------------------------------
        # STEP 7: Alternative Handling (If exact matches are empty)
        # -------------------------------------------------------------
        if not validation_res.exact_matches:
            return alternative_handler.generate_alternative_response(
                user_message=user_message,
                intent=merged_context,
                validation_res=validation_res,
                current_cart=updated_cart,
                audit_logger=audit_logger
            )

        # -------------------------------------------------------------
        # STEP 6 & 8: Recommendation Scoring, Ranking, and Response Framing
        # -------------------------------------------------------------
        candidates = validation_res.exact_matches
        audit_logger.log("CATALOG_SEARCH", f"Found {len(candidates)} candidate products.")

        ranked_results = ranking_engine.rank_catalog(candidates, query=user_message, max_price=merged_context.get("max_price"))
        top_ranked = ranked_results[:3]

        audit_logger.log("RANKING_COMPLETE", f"Top match: '{top_ranked[0]['product']['name']}' (Score: {top_ranked[0]['total_score']}/100)")

        suggested_products = [r["product"] for r in top_ranked]
        best_match = top_ranked[0]
        best_prod = best_match["product"]

        max_p = merged_context.get("max_price")
        budget_str = f" under ₹{int(max_p):,}" if max_p else ""
        header = f"Here are the top options{budget_str} tailored to your requirements:"

        response_text = f"🤖 **RazorFlow AI Recommendation Engine:** {header}\n\n"
        response_text += f"🏆 **BEST MATCH:** **{best_prod['name']}** — **₹{best_prod['price']:,}**\n"
        response_text += f"⭐ **Rating & Volume:** {best_prod['rating']}★ from {best_prod['reviews_count']:,} customer reviews\n\n"
        response_text += f"{best_match['explanation']}\n\n"

        if len(top_ranked) > 1:
            response_text += "--- \n**Other Strong Options:**\n"
            for idx, item in enumerate(top_ranked[1:], 2):
                p = item["product"]
                response_text += f"{idx}. **{p['name']}** — **₹{p['price']:,}** (⭐{p['rating']} | {p['reviews_count']:,} reviews)\n"

        # Contextual Cross-Selling (ONLY when valid recommendations exist)
        if best_prod.get("category") == "Laptops":
            cross_sells = search_catalog(category="Accessories", max_price=3000)
            if cross_sells:
                cs = cross_sells[0]
                response_text += (
                    f"\n\n💡 **Contextual Cross-Sell Suggestion:**\n"
                    f"Pair this laptop with **{cs['name']}** for **₹{cs['price']:,}** ({cs['description'][:60]}...)."
                )

        analytics_service.log_query_analytics(user_message, merged_context, len(suggested_products), suggested_products)

        return {
            "response": response_text,
            "cart": updated_cart,
            "products": suggested_products,
            "confirmation_required": False,
            "active_order": None,
            "context": merged_context,
            "audit_logs": audit_logger.get_logs()
        }

recommendation_pipeline = RecommendationPipeline()
