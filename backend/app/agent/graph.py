import re
from typing import Dict, Any, List
from app.agent.tools import search_catalog, manage_cart, create_razorpay_order
from app.services.analytics_service import analytics_service

class RazorFlowAgent:
    """
    Agentic E-Commerce Engine implementing budget-aware search, 
    contextual cross-selling/upselling, cart management, and 
    Deterministic Human-in-the-Loop Guardrail before Razorpay Order creation.
    """
    
    @staticmethod
    def process_message(user_message: str, current_cart: List[Dict[str, Any]], confirmed_pay: bool = False) -> Dict[str, Any]:
        user_text = user_message.lower().strip()
        
        # Log customer intent keyword into Analytics Service
        analytics_service.log_intent(user_message)
        
        response_text = ""
        suggested_products = []
        updated_cart = list(current_cart)
        confirmation_required = False
        active_order = None
        
        # Check total cart value
        cart_summary = manage_cart(updated_cart, action="get", product_id="")
        
        # -------------------------------------------------------------
        # 1. Deterministic Guardrail Check: Payment Execution Trigger
        # -------------------------------------------------------------
        is_pay_intent = any(k in user_text for k in ["buy", "checkout", "pay", "order", "purchase", "proceed"])
        is_confirmation = confirmed_pay or any(k in user_text for k in ["yes", "confirm", "proceed to pay", "approve", "lets do it", "let's pay"])
        
        if is_confirmation and cart_summary["item_count"] > 0:
            # User explicitly confirmed payment -> Execute create_razorpay_order tool
            total_paise = cart_summary["total_paise"]
            order_res = create_razorpay_order(amount_paise=total_paise, currency="INR")
            
            response_text = (
                f"✅ **Razorpay Order Generated!**\n\n"
                f"Order ID: `{order_res['order_id']}`\n"
                f"Total Amount: **₹{cart_summary['total_inr']:,}** ({total_paise} paise)\n\n"
                f"Click the checkout button below to launch the secure **Razorpay Checkout Modal**."
            )
            active_order = {
                "order_id": order_res["order_id"],
                "amount_paise": total_paise,
                "amount_inr": cart_summary["total_inr"],
                "currency": "INR",
                "key_id": order_res.get("key_id", ""),
                "items": cart_summary["cart"]
            }
            return {
                "response": response_text,
                "cart": cart_summary["cart"],
                "products": [],
                "confirmation_required": False,
                "active_order": active_order
            }
            
        elif is_pay_intent and cart_summary["item_count"] > 0:
            # Deterministic Guardrail Trigger: Ask for explicit user confirmation before order generation
            confirmation_required = True
            response_text = (
                f"⚠️ **Payment Confirmation Required (Deterministic Guardrail)**\n\n"
                f"You have **{cart_summary['item_count']} item(s)** in your cart totaling **₹{cart_summary['total_inr']:,}**.\n\n"
                f"Would you like to generate the authentic Razorpay Checkout Order now?"
            )
            return {
                "response": response_text,
                "cart": cart_summary["cart"],
                "products": [],
                "confirmation_required": True,
                "active_order": None
            }

        # -------------------------------------------------------------
        # 2. Add to Cart / Remove from Cart Actions
        # -------------------------------------------------------------
        if "add" in user_text or "cart" in user_text:
            # Match product names or IDs
            catalog = search_catalog()
            matched_prod = None
            for p in catalog:
                if p["id"].lower() in user_text or p["name"].lower() in user_text or any(tag in user_text for tag in p["tags"]):
                    matched_prod = p
                    break
            
            if matched_prod:
                res = manage_cart(updated_cart, action="add", product_id=matched_prod["id"], quantity=1)
                updated_cart = res["cart"]
                
                # Context-aware upselling/cross-selling recommendation based on remaining budget
                cross_sell_text = ""
                remaining_budget = 60000 - res["total_inr"]
                if remaining_budget > 1000:
                    accessories = search_catalog(category="Accessories", max_price=remaining_budget)
                    if accessories:
                        rec = accessories[0]
                        cross_sell_text = (
                            f"\n\n💡 **Recommended Accessory within your budget:**\n"
                            f"Add **{rec['name']}** for **₹{rec['price']:,}** (Fits remaining budget)."
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
                    "active_order": None
                }

        # -------------------------------------------------------------
        # 3. Conversational Catalog Search & Budget Awareness
        # -------------------------------------------------------------
        # Extract max budget from query if present (e.g. "under 60,000" or "under ₹60000" or "below 50000")
        max_price = None
        budget_match = re.search(r'(?:under|below|max|budget of|within|rs\.?|₹)?\s*(\d{1,2}(?:,\d{2})*(?:,\d{3})?|\d{4,6})', user_text)
        if budget_match:
            try:
                num_str = budget_match.group(1).replace(",", "")
                val = float(num_str)
                if val >= 500: # reasonable price floor
                    max_price = val
            except ValueError:
                pass
                
        # Determine category if query specifies laptops, headphones, mouse, etc.
        category = None
        if "laptop" in user_text or "computer" in user_text:
            category = "Laptops"
        elif "headphone" in user_text or "audio" in user_text or "earphone" in user_text:
            category = "Audio"
        elif "mouse" in user_text or "keyboard" in user_text or "sleeve" in user_text or "hub" in user_text:
            category = "Accessories"
        elif "monitor" in user_text or "screen" in user_text or "display" in user_text:
            category = "Monitors"

        products = search_catalog(query=user_message, max_price=max_price, category=category)
        
        if not products and (max_price or category):
            # Fallback relaxation
            products = search_catalog(query=user_message, category=category)
            
        if not products:
            # Return general catalog
            products = search_catalog()[:3]

        suggested_products = products[:3]
        
        # Build contextual response
        if max_price:
            budget_formatted = f"under ₹{int(max_price):,}"
        else:
            budget_formatted = ""
            
        header = f"Here are top recommended options {budget_formatted} tailored for your needs:" if budget_formatted else "Here are top products from our catalog:"
        
        response_text = f"🤖 **RazorFlow Agent:** {header}\n\n"
        for idx, p in enumerate(suggested_products, 1):
            response_text += f"{idx}. **{p['name']}** — **₹{p['price']:,}** (Rating: ⭐{p['rating']})\n   _{p['description']}_\n\n"
            
        # Cross-sell recommendation logic
        if suggested_products:
            first_p = suggested_products[0]
            if first_p["category"] == "Laptops":
                cross_sells = search_catalog(category="Accessories", max_price=3000)
                if cross_sells:
                    cs = cross_sells[0]
                    response_text += (
                        f"💡 **Suggested Upsell/Cross-sell:**\n"
                        f"Pair this laptop with the **{cs['name']}** for **₹{cs['price']:,}** to protect your setup!"
                    )

        return {
            "response": response_text,
            "cart": updated_cart,
            "products": suggested_products,
            "confirmation_required": False,
            "active_order": None
        }

agent_engine = RazorFlowAgent()
