import os
import json
import re
from typing import Dict, Any, List, Optional
from app.agent.catalog_registry import catalog_registry

class AIService:
    """
    Modular AI Agent Service supporting optional Google Gemini API free-tier model integration
    for structured JSON shopping intent extraction with deterministic fallback.
    """
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.use_llm = bool(self.api_key and self.api_key.startswith("AIza"))

    def extract_structured_intent(self, query: str) -> Dict[str, Any]:
        """
        Converts natural language shopping query into structured JSON intent using Gemini API or deterministic fallback.
        Strictly general-purpose: extracts any product category, intent type, and explicit attributes.
        """
        if self.use_llm:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(
                    "gemini-1.5-flash",
                    generation_config={"response_mime_type": "application/json"}
                )
                
                prompt = (
                    "You are a general-purpose e-commerce AI intent parser. Extract structured shopping intent from the user query into JSON.\n"
                    "Do NOT assume or limit categories to predefined lists. Extract whatever product/category the user is asking for.\n"
                    "Output JSON schema:\n"
                    "{\n"
                    '  "intent_type": "discovery | recommendation | comparison | search_filter | add_to_cart | remove_from_cart | update_cart | view_cart | checkout | product_info | budget_shopping | attribute_shopping | category_shopping",\n'
                    '  "category": "exact product category requested (e.g. running shoes, laptop bag, coffee maker, headphones, laptop, monitor, kurta set, smartwatch, t-shirt, etc.) or null",\n'
                    '  "attributes": {\n'
                    '    "color": "color or null",\n'
                    '    "gender": "female/male/unisex or null",\n'
                    '    "size": "size or null",\n'
                    '    "brand": "brand name or null",\n'
                    '    "model": "model name or null",\n'
                    '    "material": "material or null",\n'
                    '    "style": "style or null",\n'
                    '    "type": "type or null",\n'
                    '    "age_group": "age group or null",\n'
                    '    "compatibility": "compatibility or null",\n'
                    '    "features": ["list of explicitly requested features"],\n'
                    '    "specs": {},\n'
                    '    "use_case": "use case or null",\n'
                    '    "rating": null\n'
                    '  },\n'
                    '  "budget": float_max_price_or_null,\n'
                    '  "quantity": int_requested_quantity_default_1\n'
                    "}\n\n"
                    f"User Query: '{query}'"
                )
                res = model.generate_content(prompt)
                if res and res.text:
                    parsed = json.loads(res.text.strip())
                    if isinstance(parsed, dict) and ("category" in parsed or "intent_type" in parsed):
                        return parsed
            except Exception as ex:
                print(f"[AIService] Gemini API structured intent extraction fallback: {ex}")

        return self._deterministic_intent_parser(query)

    def _deterministic_intent_parser(self, query: str) -> Dict[str, Any]:
        user_text = query.lower().strip()
        
        # 1. Budget extraction
        budget = None
        k_match = re.search(r'(\d+)\s*k\b', user_text)
        if k_match:
            budget = float(k_match.group(1)) * 1000.0
        else:
            matches = re.findall(r'(?:under|below|max|budget|within|rs\.?|₹)?\s*([\d,]{4,8})', user_text)
            for m in matches:
                clean_num = m.replace(",", "").strip()
                if clean_num.isdigit() and float(clean_num) >= 500:
                    budget = float(clean_num)
                    break

        # 2. Color extraction
        color = None
        for c in ["red", "blue", "green", "yellow", "purple", "pink", "orange", "gold", "silver", "rgb", "black", "white", "gray", "grey", "brown", "navy"]:
            if re.search(r'\b' + c + r'\b', user_text):
                color = c
                break

        # 3. Gender extraction
        gender = None
        if any(w in user_text for w in ["women", "womens", "women's", "female", "lady", "ladies"]):
            gender = "female"
        elif any(w in user_text for w in ["men", "mens", "men's", "male", "gentlemen"]):
            gender = "male"
        elif "unisex" in user_text:
            gender = "unisex"

        # 4. Size extraction
        size = None
        size_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:inch|\")?', user_text)
        if size_match and size_match.group(1) in ["13.3", "13.6", "14", "15.6", "17.3", "27"]:
            size = size_match.group(1)
        else:
            for s in ["small", "medium", "large", "xl", "xxl"]:
                if re.search(r'\b' + s + r'\b', user_text):
                    size = s
                    break

        # 5. Brand extraction
        brand = catalog_registry.detect_brand(user_text)

        # 6. Material extraction
        material = None
        for mat in ["leather", "neoprene", "aluminum", "aluminium", "plastic", "cotton", "wool", "metal", "mesh", "foam"]:
            if re.search(r'\b' + mat + r'\b', user_text):
                material = mat
                break

        # 7. Features extraction
        features = []
        for feat in ["wireless", "anc", "noise cancelling", "4k", "oled", "mechanical", "water-resistant", "water resistant", "ergonomic", "bluetooth", "144hz", "vertical", "rechargeable"]:
            if feat in user_text:
                features.append(feat)

        # 8. Use case extraction
        use_case = None
        for uc in ["coding", "programming", "gaming", "office", "travel", "student", "developer", "data science", "ai development"]:
            if uc in user_text:
                use_case = uc
                break

        # 9. Dynamic Category / Head Noun extraction via CatalogRegistry
        category = self._extract_dynamic_category(user_text)

        # 10. Intent type determination
        intent_type = "product_search"
        if any(k in user_text for k in ["compare", "versus", " vs ", "difference"]):
            intent_type = "comparison"
        elif any(k in user_text for k in ["recommend", "suggestion", "best", "top"]):
            intent_type = "recommendation"
        elif any(k in user_text for k in ["remove", "delete", "take out"]):
            intent_type = "remove_from_cart"
        elif any(k in user_text for k in ["add to cart", "put in cart", "buy this"]):
            intent_type = "add_to_cart"
        elif any(k in user_text for k in ["view cart", "show cart", "whats in cart"]):
            intent_type = "view_cart"
        elif budget is not None:
            intent_type = "budget_shopping"
        elif color or brand or size or features:
            intent_type = "attribute_shopping"

        return {
            "intent_type": intent_type,
            "category": category,
            "attributes": {
                "color": color,
                "gender": gender,
                "size": size,
                "brand": brand,
                "model": None,
                "material": material,
                "style": None,
                "type": None,
                "age_group": None,
                "compatibility": None,
                "features": features,
                "specs": {},
                "use_case": use_case,
                "rating": None
            },
            "budget": budget,
            "quantity": 1
        }

    def _extract_dynamic_category(self, user_text: str) -> Optional[str]:
        """
        Dynamically extracts the requested product category or head noun from query text
        using CatalogRegistry and NLP patterns.
        """
        from app.agent.catalog_registry import catalog_registry

        # 1. Try matching with CatalogRegistry
        matched = catalog_registry.get_matching_category(user_text)
        if matched:
            # Check for sub-category noun specificity (e.g. "laptop carry bag" vs "laptop")
            if any(b in user_text for b in ["bag", "sleeve", "case", "pouch", "backpack", "carry bag"]):
                return "bag"
            elif any(m in user_text for m in ["mouse", "mice"]):
                return "mouse"
            elif any(k in user_text for k in ["keyboard", "keycaps"]):
                return "keyboard"
            elif any(c in user_text for c in ["cooling pad", "cooler"]):
                return "cooler"
            elif any(h in user_text for h in ["usb-c hub", "dongle", "adapter", "hub"]):
                return "hub"
            return matched

        # 2. Known product noun patterns
        multi_words = [
            "running shoes", "kurta set", "cooling pad", "laptop bag", "laptop sleeve",
            "mechanical keyboard", "wireless mouse", "gaming laptop", "smart watch",
            "coffee maker", "water bottle", "air conditioner", "desk lamp"
        ]
        for mw in multi_words:
            if mw in user_text:
                return mw

        patterns = [
            (r'\b(shoes?|sneakers?|footwear|boots?|sandals?)\b', 'shoes'),
            (r'\b(kurta\s*set|kurta|kurtis?|shirts?|t-shirts?|tshirts?|jackets?|hoodies?|pants?|jeans?|trousers?|dress(?:es)?|saree)\b', 'kurta set'),
            (r'\b(bags?|sleeves?|backpacks?|cases?|pouches?)\b', 'bag'),
            (r'\b(mice|mouse)\b', 'mouse'),
            (r'\b(keyboards?|keycaps?)\b', 'keyboard'),
            (r'\b(coolers?|cooling)\b', 'cooler'),
            (r'\b(hubs?|dongles?|adapters?)\b', 'hub'),
            (r'\b(watch(?:es)?|smartwatch(?:es)?|timepiece(?:s)?)\b', 'watch'),
            (r'\b(headphones?|earphones?|headsets?|earbuds?|audio)\b', 'audio'),
            (r'\b(monitors?|displays?|screens?)\b', 'monitor'),
            (r'\b(phones?|smartphones?|mobiles?|cellphones?)\b', 'phone'),
            (r'\b(laptops?|notebooks?|macbooks?|computers?)\b', 'laptop')
        ]

        for pat, val in patterns:
            m = re.search(pat, user_text)
            if m:
                return val(m) if callable(val) else val

        # Noun extraction if explicit product inquiry verbs exist
        inquiry_verbs = ["need", "want", "looking for", "find", "show", "buy", "search for"]
        if any(v in user_text for v in inquiry_verbs):
            stop_words = {
                "i", "need", "want", "looking", "for", "a", "an", "the", "under", "below",
                "rs", "inr", "show", "me", "find", "best", "good", "great", "top", "also",
                "only", "please", "can", "you", "my", "this", "that", "it", "with", "k"
            }
            spec_words = {
                "ram", "ssd", "storage", "cpu", "gpu", "rtx", "intel", "amd", "gb", "tb",
                "mhz", "hz", "oled", "fhd", "4k", "wireless", "anc", "bluetooth", "red",
                "blue", "green", "black", "white", "gray", "cheap", "fast", "vertical",
                "water-resistant", "ergonomic", "mechanical"
            }
            words = [w.strip(".,!?") for w in user_text.split() if w.strip(".,!?") not in stop_words and not w.isdigit()]
            if words:
                for w in reversed(words):
                    if len(w) > 2 and w not in spec_words:
                        return w

        return None

    def generate_recommendation_reasoning(self, query: str, best_match: Dict[str, Any], candidates: List[Dict[str, Any]]) -> Optional[str]:
        if not self.use_llm:
            return None

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            
            prompt = (
                f"Customer Query: '{query}'\n"
                f"Recommended Product: {best_match.get('name')} (Price: ₹{best_match.get('price')}, Rating: {best_match.get('rating')}★)\n"
                f"Provide a concise, professional, 2-sentence explanation of why this product is the best match for the user's budget and requirements."
            )
            res = model.generate_content(prompt)
            return res.text.strip() if res and res.text else None
        except Exception as ex:
            print(f"[AIService] Gemini API fallback to deterministic engine: {ex}")
            return None

    def generate_growth_recommendations(self, aggregated_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Uses Gemini API (gemini-1.5-flash) with structured JSON mode to analyze aggregated
        merchant data and output 3 growth recommendations (insight, action, impact).
        """
        if self.use_llm:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                model = genai.GenerativeModel(
                    "gemini-1.5-flash",
                    generation_config={"response_mime_type": "application/json"}
                )

                prompt = (
                    "You are a Senior E-Commerce Growth Strategist AI. Analyze the following real-time merchant data:\n"
                    f"{json.dumps(aggregated_data, indent=2)}\n\n"
                    "Identify patterns across high demand, unfulfilled searches, conversion friction, and product trends.\n"
                    "Generate exactly 3 actionable growth recommendations in JSON array format.\n"
                    "Output JSON Schema:\n"
                    "[\n"
                    "  {\n"
                    '    "insight": "Factual pattern insight based ONLY on real data",\n'
                    '    "action": "Specific recommended merchant action",\n'
                    '    "impact": "Factual quantitative impact if computable, or qualitative impact (DO NOT invent fake percentages)"\n'
                    "  }\n"
                    "]"
                )
                res = model.generate_content(prompt)
                if res and res.text:
                    parsed = json.loads(res.text.strip())
                    if isinstance(parsed, list) and len(parsed) > 0:
                        return parsed[:3]
            except Exception as ex:
                print(f"[AIService] Gemini API growth recommendations fallback: {ex}")

        return self._deterministic_growth_analyzer(aggregated_data)

    def _deterministic_growth_analyzer(self, aggregated_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        actions = []
        cat_demand = aggregated_data.get("categories_demand", [])
        unfulfilled = aggregated_data.get("unfulfilled_requests", [])
        friction = aggregated_data.get("high_demand_low_conversion", [])
        top_prods = aggregated_data.get("top_products", [])

        if cat_demand:
            top_cat = cat_demand[0]
            pct = top_cat.get("percentage", 0)
            top_prod_name = top_prods[0]["name"] if top_prods else "featured items"
            actions.append({
                "insight": f"High customer demand for {top_cat['category']} ({pct}% of total customer searches)",
                "action": f"Promote top-rated {top_prod_name} in AI recommendation highlights",
                "impact": f"+{round(pct * 0.4, 1)}% conversion opportunity"
            })

        if unfulfilled:
            top_un = unfulfilled[0]
            actions.append({
                "insight": f"Unfulfilled customer demand for '{top_un['query']}' ({top_un['count']} missed searches)",
                "action": f"Stock and feature '{top_un['query']}' in store inventory",
                "impact": f"+{top_un['count']} potential orders lift"
            })

        if friction:
            f_prod = friction[0]
            actions.append({
                "insight": f"'{f_prod['name']}' has high search volume ({f_prod['searches']} views) but low conversion ({f_prod['conversion']})",
                "action": f"Apply a promotional discount or bundle offer on {f_prod['name']}",
                "impact": "Expected conversion rate improvement"
            })

        if not actions:
            actions.append({
                "insight": "No sufficient data yet",
                "action": "Collect more customer chat sessions to generate AI recommendations",
                "impact": "Awaiting data"
            })

        return actions[:3]

ai_service = AIService()
