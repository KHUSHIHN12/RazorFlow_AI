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
        # 6. Add to Cart / Cart Management Trigger
        # -------------------------------------------------------------
        if "add" in user_text or "cart" in user_text:
            audit_logger.log("CART_ACTION_TRIGGERED", "Processing add to cart request.")
            intent_meta = ranking_engine.parse_intent(user_message)
            matched_prod = None
            
            # Use intent category & head noun to search candidates
            head_n = intent_meta.get("head_noun")
            candidates = search_catalog(query=head_n or user_message, category=intent_meta.get("category"))
            if not candidates and head_n:
                candidates = search_catalog(query=head_n)
            if not candidates:
                candidates = search_catalog()
                
            if "second" in user_text or "2nd" in user_text or "number 2" in user_text:
                ranked = ranking_engine.rank_catalog(candidates, query=user_message)
                if len(ranked) >= 2:
                    matched_prod = ranked[1]["product"]
            elif "first" in user_text or "1st" in user_text or "recommended" in user_text:
                ranked = ranking_engine.rank_catalog(candidates, query=user_message)
                if ranked:
                    matched_prod = ranked[0]["product"]
            else:
                for p in candidates:
                    p_corpus = f"{p['id']} {p['name']} {' '.join(p.get('tags', []))}".lower()
                    if head_n and head_n in p_corpus:
                        matched_prod = p
                        break
                    elif p["id"].lower() in user_text or p["name"].lower() in user_text:
                        matched_prod = p
                        break

            if not matched_prod and candidates:
                matched_prod = candidates[0]
            
            if matched_prod:
                res = manage_cart(updated_cart, action="add", product_id=matched_prod["id"], quantity=1)
                updated_cart = res["cart"]
                audit_logger.log("CART_MUTATED", f"Added '{matched_prod['name']}' to cart. Total items: {res['item_count']}")
                
                # Contextual Cross-Selling
                cross_sell_text = ""
                rem_budget = 60000 - res["total_inr"]
                if matched_prod["category"] == "Laptops":
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
                    f"🛒 Added **{matched_prod['name']}** (₹{matched_prod['price']:,}) to your cart!\n"
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
        audit_logger.log("INTENT_PARSED", f"Focus: {intent['focus_area']}, Max Price: {intent['max_price']}, Category: {intent['category']}, Head Noun: {intent['head_noun']}")
        
        # 1. Primary Category & Head Noun Search
        candidates = []
        head_n = intent.get("head_noun")
        cat = intent.get("category")
        max_p = intent.get("max_price")

        if head_n:
            candidates = search_catalog(query=head_n, max_price=max_p, category=cat)
            all_cat_items = search_catalog(query=head_n, category=cat)
        elif cat:
            candidates = search_catalog(category=cat, max_price=max_p)
            all_cat_items = search_catalog(category=cat)
        else:
            candidates = search_catalog(query=user_message, max_price=max_p)
            all_cat_items = candidates

        # 2. Out-Of-Catalog Category Handling (e.g. "smartwatch")
        if not all_cat_items and (head_n or cat):
            target_name = head_n or user_message
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

        # 3. Out-Of-Budget Handling (Products exist in category, but all exceed max_price)
        if not candidates and max_p and all_cat_items:
            closest_prod = ranking_engine.find_closest_above_budget(all_cat_items, max_p)
            if closest_prod:
                diff_amount = float(closest_prod["price"]) - max_p
                audit_logger.log("OUT_OF_BUDGET_ALTERNATIVE", f"Budget ₹{max_p:,.0f} too low. Closest option: '{closest_prod['name']}' at ₹{closest_prod['price']:,}.")
                
                specs = closest_prod.get("specs", {})
                spec_str = f"{specs.get('processor', 'High performance')} with {specs.get('ram', '16GB RAM')}"
                
                response_text = (
                    f"⚠️ **No Suitable Products Found Within Your Budget (₹{max_p:,.0f}):**\n\n"
                    f"I couldn't find a {intent.get('focus_area', '')} {cat or head_n or 'product'} meeting your exact requirements under **₹{max_p:,.0f}**.\n\n"
                    f"💡 **Closest Available Alternative:**\n"
                    f"• **{closest_prod['name']}** — **₹{closest_prod['price']:,}** (⭐ {closest_prod.get('rating', 4.5)}★ from {closest_prod.get('reviews_count', 100):,} reviews)\n"
                    f"• **Price Difference:** **₹{diff_amount:,.0f}** above your budget\n"
                    f"• **Key Value:** {spec_str}\n\n"
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

        if not candidates:
            candidates = search_catalog()

        audit_logger.log("CATALOG_SEARCH", f"Found {len(candidates)} candidate products.")
        
        ranked_results = ranking_engine.rank_catalog(candidates, query=user_message, max_price=max_p)
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

        return {
            "response": response_text,
            "cart": updated_cart,
            "products": suggested_products,
            "confirmation_required": False,
            "active_order": None,
            "audit_logs": audit_logger.get_logs()
        }

agent_engine = RazorFlowAgent()
