import re
from typing import Dict, Any, List, Optional
from app.agent.tools import search_catalog, manage_cart, create_razorpay_order, getProductDetails, compareProducts, analyzeReviews
from app.agent.ranking_engine import ranking_engine
from app.agent.bundle_engine import bundle_engine
from app.agent.audit_logger import audit_logger
from app.services.analytics_service import analytics_service

class RazorFlowAgent:
    """
    Intelligent Agentic Commerce Engine for CommercePilot AI.
    
    Orchestrates Intent Understanding, Multi-Criteria Product Decision Engine,
    Goal-Based Setup Bundling, Review Sentiment Analysis, Contextual Cross-Selling,
    Selective Cart Checkout, and Deterministic Human-in-the-Loop Payment Guardrails.
    """
    
    @staticmethod
    def process_message(user_message: str, current_cart: List[Dict[str, Any]], confirmed_pay: bool = False) -> Dict[str, Any]:
        user_text = user_message.lower().strip()
        audit_logger.clear()
        
        # Log customer intent into Analytics Service
        analytics_service.log_intent(user_message)
        audit_logger.log("INTENT_RECEIVED", f"Customer message: '{user_message}'")
        
        response_text = ""
        suggested_products = []
        updated_cart = [item.copy() for item in current_cart]
        confirmation_required = False
        active_order = None
        bundle_data = None

        # Calculate selected items vs all cart items
        selected_items = [i for i in updated_cart if i.get("selected") is True]
        selected_inr = sum(i["price"] * i["quantity"] for i in selected_items)
        selected_paise = sum(i["price_paise"] * i["quantity"] for i in selected_items)
        
        # -------------------------------------------------------------
        # 1. Natural Language Cart Selection ("buy only the laptop", "buy this laptop", etc.)
        # -------------------------------------------------------------
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
                selected_items = matched_items
                selected_inr = sum(i["price"] * i["quantity"] for i in selected_items)
                selected_paise = sum(i["price_paise"] * i["quantity"] for i in selected_items)
                
                item_names = ", ".join([f"{i['name']} (₹{i['price']:,})" for i in selected_items])
                confirmation_required = True
                audit_logger.log("SELECTION_UPDATED", f"Selected {len(selected_items)} item(s) totaling ₹{selected_inr:,}. Prompting for confirmation.")
                
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
                    "audit_logs": audit_logger.get_logs()
                }

        # -------------------------------------------------------------
        # 2. Contextual Cross-Sell / Inquiry Pre-check
        # -------------------------------------------------------------
        is_cross_sell_query = any(k in user_text for k in ["what else", "cross sell", "accessory", "complementary", "should i buy with", "what accessories"])
        
        if is_cross_sell_query:
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
                "audit_logs": audit_logger.get_logs()
            }

        # -------------------------------------------------------------
        # 3. Deterministic Guardrail Check: Payment Execution Trigger
        # -------------------------------------------------------------
        is_pay_intent = any(k in user_text for k in ["buy", "checkout", "pay", "order", "purchase", "proceed"])
        is_explicit_confirm = confirmed_pay or any(k in user_text for k in ["yes", "confirm", "proceed to pay", "approve", "lets do it", "let's pay", "proceed with order"])
        
        if (is_pay_intent or is_explicit_confirm) and len(selected_items) == 0:
            audit_logger.log("CHECKOUT_FAILED", "No items selected in Buying List for checkout.")
            response_text = (
                "⚠️ **No items selected for checkout.**\n\n"
                "Your buying list is currently empty. Please select at least one item from your cart to proceed with checkout."
            )
            return {
                "response": response_text,
                "cart": updated_cart,
                "products": [],
                "confirmation_required": False,
                "active_order": None,
                "audit_logs": audit_logger.get_logs()
            }

        if is_explicit_confirm and len(selected_items) > 0:
            audit_logger.log("GUARDRAIL_PASSED", f"User explicitly confirmed payment for {len(selected_items)} selected item(s). Calling create_razorpay_order.")
            order_res = create_razorpay_order(amount_paise=selected_paise, currency="INR")
            
            response_text = (
                f"✅ **Razorpay Order Generated!**\n\n"
                f"Order ID: `{order_res['order_id']}`\n"
                f"Selected Items: **{len(selected_items)} item(s)**\n"
                f"Total Selected Amount: **₹{selected_inr:,}** ({selected_paise} paise)\n\n"
                f"Click the button below to launch the secure **Razorpay Checkout Modal**."
            )
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
                "response": response_text,
                "cart": updated_cart,
                "products": [],
                "confirmation_required": False,
                "active_order": active_order,
                "audit_logs": audit_logger.get_logs()
            }
            
        elif is_pay_intent and len(selected_items) > 0:
            confirmation_required = True
            audit_logger.log("GUARDRAIL_TRIGGERED", "Financial action requested. Prompting for explicit user confirmation.")
            item_names = ", ".join([f"{i['name']}" for i in selected_items])
            response_text = (
                f"⚠️ **Payment Confirmation Required (Deterministic Guardrail)**\n\n"
                f"You have selected **{len(selected_items)} item(s)** ({item_names}) for checkout totaling **₹{selected_inr:,}**.\n\n"
                f"Would you like me to proceed to generate the authentic Razorpay Checkout Order?"
            )
            return {
                "response": response_text,
                "cart": updated_cart,
                "products": [],
                "confirmation_required": True,
                "active_order": None,
                "audit_logs": audit_logger.get_logs()
            }

        # -------------------------------------------------------------
        # 4. Goal-Based Shopping Bundle Request
        # -------------------------------------------------------------
        if any(k in user_text for k in ["setup", "bundle", "complete package", "complete programming setup", "student setup"]):
            audit_logger.log("GOAL_ENGINE_TRIGGERED", "Constructing multi-product setup bundle.")
            intent_meta = ranking_engine.parse_intent(user_message)
            budget_val = intent_meta.get("max_price") or 70000.0
            
            bundle_res = bundle_engine.create_goal_bundle(user_message, total_budget=budget_val)
            bundle_data = bundle_res
            suggested_products = bundle_res["items"]
            
            response_text = bundle_res["explanation"]
            audit_logger.log("BUNDLE_CREATED", f"Total bundle cost: ₹{bundle_res['total_cost']:,}")

            return {
                "response": response_text,
                "cart": updated_cart,
                "products": suggested_products,
                "bundle_data": bundle_data,
                "confirmation_required": False,
                "active_order": None,
                "audit_logs": audit_logger.get_logs()
            }

        # -------------------------------------------------------------
        # 5. Product Comparison Request
        # -------------------------------------------------------------
        if any(k in user_text for k in ["compare", "versus", " vs ", "difference"]):
            audit_logger.log("COMPARISON_ENGINE_TRIGGERED", "Executing side-by-side product comparison.")
            laptops = search_catalog(category="Laptops")
            ranked_laptops = ranking_engine.rank_catalog(laptops, query=user_message)
            top_two = [r["product"] for r in ranked_laptops[:2]]
            
            if len(top_two) >= 2:
                p1, p2 = top_two[0], top_two[1]
                response_text = (
                    f"⚖️ **Side-by-Side Product Comparison:**\n\n"
                    f"1. **{p1['name']}** — **₹{p1['price']:,}** (⭐ {p1['rating']} | {p1['reviews_count']:,} reviews)\n"
                    f"   • Processor: {p1['specs'].get('processor', 'N/A')}\n"
                    f"   • RAM: {p1['specs'].get('ram', 'N/A')}\n"
                    f"   • Storage: {p1['specs'].get('storage', 'N/A')}\n"
                    f"   • Key Strength: {p1.get('review_themes', {}).get('positive', ['Great overall'])[0]}\n\n"
                    f"2. **{p2['name']}** — **₹{p2['price']:,}** (⭐ {p2['rating']} | {p2['reviews_count']:,} reviews)\n"
                    f"   • Processor: {p2['specs'].get('processor', 'N/A')}\n"
                    f"   • RAM: {p2['specs'].get('ram', 'N/A')}\n"
                    f"   • Storage: {p2['specs'].get('storage', 'N/A')}\n"
                    f"   • Key Strength: {p2.get('review_themes', {}).get('positive', ['Great overall'])[0]}\n\n"
                    f"💡 **Recommendation:** Choose **{p1['name']}** if you prioritize performance & battery life, or **{p2['name']}** for maximum budget savings."
                )
                return {
                    "response": response_text,
                    "cart": updated_cart,
                    "products": top_two,
                    "confirmation_required": False,
                    "active_order": None,
                    "audit_logs": audit_logger.get_logs()
                }

        # -------------------------------------------------------------
        # 6. Cart Action Intelligence (ADD, REMOVE, UPDATE, VIEW)
        # -------------------------------------------------------------
        from app.agent.cart_intent_detector import CartIntentDetector
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
                    "audit_logs": audit_logger.get_logs()
                }

            elif action_type == "REMOVE":
                if not target_item:
                    response_text = f"⚠️ Could not find the requested item to remove in your cart."
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
                    "audit_logs": audit_logger.get_logs()
                }

            elif action_type == "UPDATE":
                if not target_item:
                    response_text = f"⚠️ Could not find the requested item to update in your cart."
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
                    "audit_logs": audit_logger.get_logs()
                }

            elif action_type == "ADD":
                matched_prod = target_item
                if not matched_prod:
                    candidates = search_catalog(query=user_message)
                    if candidates:
                        matched_prod = candidates[0]
                
                if matched_prod:
                    prod_id = matched_prod.get("product_id") or matched_prod.get("id")
                    prod_name = matched_prod.get("name")
                    prod_price = matched_prod.get("price", 0)
                    prod_cat = matched_prod.get("category", "")
                    
                    res = manage_cart(updated_cart, action="add", product_id=prod_id, quantity=req_qty)
                    updated_cart = res["cart"]
                    audit_logger.log("CART_MUTATED", f"Added '{prod_name}' to cart. Total items: {res['item_count']}")

                    # Contextual Cross-Selling
                    cross_sell_text = ""
                    rem_budget = 60000 - res["total_inr"]
                    if prod_cat == "Laptops":
                        if "gaming" in matched_prod.get("tags", []):
                            coolers = search_catalog(query="cooling pad")
                            if coolers:
                                cs = coolers[0]
                                cross_sell_text = (
                                    f"\n\n💡 **Contextual Cross-Sell Recommendation:**\n"
                                    f"Since you're purchasing a gaming laptop, a cooling pad helps maintain optimal thermals during long gaming sessions.\n"
                                    f"Add **{cs['name']}** for **₹{cs['price']:,}**!"
                                )
                        else:
                            accs = search_catalog(category="Accessories", max_price=max(3000, rem_budget))
                            if accs:
                                cs = accs[0]
                                cross_sell_text = (
                                    f"\n\n💡 **Contextual Cross-Sell Recommendation:**\n"
                                    f"Since you are purchasing a developer laptop, protect your investment with **{cs['name']}** for **₹{cs['price']:,}**!"
                                )

                    response_text = (
                        f"🛒 Added **{prod_name}** (₹{prod_price:,}) to your cart!\n"
                        f"Current Cart Total: **₹{res['total_inr']:,}** ({res['item_count']} items)."
                        f"{cross_sell_text}"
                    )
                    return {
                        "response": response_text,
                        "cart": updated_cart,
                        "products": [matched_prod],
                        "confirmation_required": False,
                        "active_order": None,
                        "audit_logs": audit_logger.get_logs()
                    }

        # -------------------------------------------------------------
        # 7. Default Flow: Intent Parsing & Product Decision Engine
        # -------------------------------------------------------------
        intent = ranking_engine.parse_intent(user_message)
        max_p = intent.get("max_price")
        
        # Log Extracted Structured Intent in Audit Trail
        attr_log_parts = []
        if intent.get("category"): attr_log_parts.append(f"category = \"{intent['category']}\"")
        if intent.get("color"): attr_log_parts.append(f"color = \"{intent['color']}\"")
        if intent.get("gender"): attr_log_parts.append(f"gender = \"{intent['gender']}\"")
        if intent.get("size"): attr_log_parts.append(f"size = \"{intent['size']}\"")
        if intent.get("brand"): attr_log_parts.append(f"brand = \"{intent['brand']}\"")
        if intent.get("max_price"): attr_log_parts.append(f"budget = {intent['max_price']}")
        
        extracted_summary = ", ".join(attr_log_parts) if attr_log_parts else "unconstrained query"
        audit_logger.log("EXTRACTED_INTENT", f"Extracted Intent: {extracted_summary}")
        audit_logger.log("PIPELINE_STAGE", "Executing: Category Filter → Attribute Filter → Budget Filter → Ranking")
        
        all_catalog_items = search_catalog()
        filtering_res = ranking_engine.filter_candidates_by_intent(all_catalog_items, intent)

        fallback_level = filtering_res["fallback_level"]
        exact_matches = filtering_res["exact_matches"]
        relaxed_attribute_matches = filtering_res["relaxed_attribute_matches"]
        relaxed_budget_matches = filtering_res["relaxed_budget_matches"]
        category_exists = filtering_res["category_exists"]
        stage1_candidates = filtering_res["stage1_candidates"]

        # Level 4 Fallback: Category not available in store catalog -> HARD STOP (Return products: [])
        if fallback_level == "no_category" or (not category_exists and (intent.get("head_noun") or intent.get("category"))):
            target_name = intent.get("head_noun") or intent.get("category") or user_message
            audit_logger.log("OUT_OF_CATALOG_UNAVAILABLE", f"No products matching '{target_name}' in catalog.")
            response_text = (
                f"⚠️ **Product Category Not Found in Catalog:**\n\n"
                f"We currently do not feature **'{target_name}'** in our store catalog.\n\n"
                f"Our available catalog features:\n"
                f"• **Laptops** (ZenBook Pro 14, ThinkPad E14, MacBook Air M2, ROG Strix G16)\n"
                f"• **Monitors** (UltraSharp 27\" 4K, Gaming 144Hz Monitor)\n"
                f"• **Audio** (Sony WH-1000XM5, ANC Headphones)\n"
                f"• **Accessories** (Ergonomic Mouse, Mechanical Keyboard, Laptop Sleeves & Bags, USB-C Hubs, Cooling Pads)\n\n"
                f"Would you like me to recommend products from any of these available categories?"
            )
            return {
                "response": response_text,
                "cart": updated_cart,
                "products": [],
                "confirmation_required": False,
                "active_order": None,
                "audit_logs": audit_logger.get_logs()
            }

        # Level 2 Fallback: Same category with relaxed optional attributes (fits budget, missing 1+ attributes)
        if fallback_level == "relaxed_attributes" and stage1_candidates:
            ranked_alts = ranking_engine.rank_alternative_candidates(stage1_candidates, intent)
            best_alt = ranked_alts[0]
            closest_prod = best_alt["product"]
            missing_attrs = best_alt["missing_attrs"]
            attr_str = ", ".join(missing_attrs) if missing_attrs else "optional preferences"
            
            audit_logger.log("ATTRIBUTE_RELAXED_FALLBACK", f"Relaxed {attr_str} in category '{closest_prod.get('category')}'. Suggesting '{closest_prod['name']}'.")
            
            specs = closest_prod.get("specs", {})
            spec_parts = [f"{k.capitalize()}: {v}" for k, v in specs.items()][:3]
            spec_str = ", ".join(spec_parts) if spec_parts else closest_prod.get("description", "")
            
            response_text = (
                f"⚠️ **No Exact Match Found for Specified Attribute(s):**\n\n"
                f"I couldn't find a {intent.get('head_noun') or intent.get('category') or 'product'} matching **{attr_str}** in our catalog.\n\n"
                f"💡 **Closest Available Alternative (Same Category - Relaxed Attributes):**\n"
                f"• **{closest_prod['name']}** — **₹{closest_prod['price']:,}** (⭐ {closest_prod.get('rating', 4.5)}★ from {closest_prod.get('reviews_count', 100):,} reviews)\n"
                f"• **Key Specifications:** {spec_str}\n\n"
                f"Would you like to view this alternative in {closest_prod.get('category', 'our catalog')}?"
            )
            return {
                "response": response_text,
                "cart": updated_cart,
                "products": [closest_prod],
                "confirmation_required": False,
                "active_order": None,
                "audit_logs": audit_logger.get_logs()
            }

        # Level 3 Fallback: Same category with minimal constraints (exceeds budget in same category)
        if fallback_level == "relaxed_budget" and relaxed_budget_matches and max_p:
            raw_budget_prods = [p[0] for p in relaxed_budget_matches]
            closest_prod = ranking_engine.find_closest_above_budget(raw_budget_prods, max_p)
            if closest_prod:
                diff_amount = float(closest_prod["price"]) - max_p
                audit_logger.log("BUDGET_RELAXED_FALLBACK", f"Budget ₹{max_p:,.0f} too low. Closest option in category '{closest_prod.get('category')}': '{closest_prod['name']}' at ₹{closest_prod['price']:,}.")
                
                specs = closest_prod.get("specs", {})
                spec_parts = [f"{k.capitalize()}: {v}" for k, v in specs.items()][:3]
                spec_str = ", ".join(spec_parts) if spec_parts else closest_prod.get("description", "")
                
                response_text = (
                    f"⚠️ **No Suitable Products Found Within Your Budget (₹{max_p:,.0f}):**\n\n"
                    f"I couldn't find a {intent.get('head_noun') or intent.get('category') or 'product'} meeting your exact requirements under **₹{max_p:,.0f}**.\n\n"
                    f"💡 **Closest Available Alternative (Same Category):**\n"
                    f"• **{closest_prod['name']}** — **₹{closest_prod['price']:,}** (⭐ {closest_prod.get('rating', 4.5)}★ from {closest_prod.get('reviews_count', 100):,} reviews)\n"
                    f"• **Price Difference:** **₹{diff_amount:,.0f}** above your budget\n"
                    f"• **Key Specifications:** {spec_str}\n\n"
                    f"Would you like me to show you details for this product around **₹{closest_prod['price']:,}**?"
                )
                return {
                    "response": response_text,
                    "cart": updated_cart,
                    "products": [closest_prod],
                    "confirmation_required": False,
                    "active_order": None,
                    "audit_logs": audit_logger.get_logs()
                }

        candidates = exact_matches if exact_matches else stage1_candidates

        audit_logger.log("CATALOG_SEARCH", f"Found {len(candidates)} candidate products.")
        
        ranked_results = ranking_engine.rank_catalog(candidates, query=user_message, max_price=intent.get("max_price"))
        top_ranked = ranked_results[:3]
        
        audit_logger.log("RANKING_COMPLETE", f"Top match: '{top_ranked[0]['product']['name']}' (Score: {top_ranked[0]['total_score']}/100)")
        
        suggested_products = [r["product"] for r in top_ranked]
        best_match = top_ranked[0]
        best_prod = best_match["product"]
        
        budget_str = f" under ₹{int(max_p):,}" if max_p else ""
        header = f"Here are the top options{budget_str} tailored to your requirements:"
        
        response_text = f"🤖 **CommercePilot AI Recommendation Engine:** {header}\n\n"
        response_text += f"🏆 **BEST MATCH:** **{best_prod['name']}** — **₹{best_prod['price']:,}**\n"
        response_text += f"⭐ **Rating & Volume:** {best_prod['rating']}★ from {best_prod['reviews_count']:,} customer reviews\n\n"
        response_text += f"{best_match['explanation']}\n\n"

        if len(top_ranked) > 1:
            response_text += "--- \n**Other Strong Options:**\n"
            for idx, item in enumerate(top_ranked[1:], 2):
                p = item["product"]
                response_text += f"{idx}. **{p['name']}** — **₹{p['price']:,}** (⭐{p['rating']} | {p['reviews_count']:,} reviews)\n"

        if best_prod["category"] == "Laptops":
            cross_sells = search_catalog(category="Accessories", max_price=3000)
            if cross_sells:
                cs = cross_sells[0]
                response_text += (
                    f"\n\n💡 **Contextual Cross-Sell Suggestion:**\n"
                    f"Pair this laptop with **{cs['name']}** for **₹{cs['price']:,}** ({cs['description'][:60]}...)."
                )

        analytics_service.log_query_analytics(user_message, intent, len(suggested_products), suggested_products)

        return {
            "response": response_text,
            "cart": updated_cart,
            "products": suggested_products,
            "confirmation_required": False,
            "active_order": None,
            "audit_logs": audit_logger.get_logs()
        }

agent_engine = RazorFlowAgent()
