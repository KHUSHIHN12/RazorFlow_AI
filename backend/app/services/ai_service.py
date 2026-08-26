import os
import json
import re
from typing import Dict, Any, List, Optional

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
        Schema:
        {
          "category": "...",
          "attributes": {
            "color": "...",
            "gender": "...",
            "size": "...",
            "brand": "...",
            "material": "...",
            "features": []
          },
          "budget": float or None,
          "quantity": 1
        }
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
                    "Extract structured shopping intent from the user query into JSON.\n"
                    "Output JSON schema:\n"
                    "{\n"
                    '  "category": "product category name (e.g. laptop, laptop bag, mouse, headphones, monitor, kurta set, phone, watch)",\n'
                    '  "attributes": {\n'
                    '    "color": "color name or null",\n'
                    '    "gender": "female/male/unisex or null",\n'
                    '    "size": "size or null",\n'
                    '    "brand": "brand name or null",\n'
                    '    "material": "material or null",\n'
                    '    "features": ["list of requested features"]\n'
                    '  },\n'
                    '  "budget": float_max_price_or_null,\n'
                    '  "quantity": int_requested_quantity_default_1\n'
                    "}\n\n"
                    f"User Query: '{query}'"
                )
                res = model.generate_content(prompt)
                if res and res.text:
                    parsed = json.loads(res.text.strip())
                    if isinstance(parsed, dict) and "category" in parsed:
                        return parsed
            except Exception as ex:
                print(f"[AIService] Gemini API structured intent extraction fallback: {ex}")

        return self._deterministic_intent_parser(query)

    def _deterministic_intent_parser(self, query: str) -> Dict[str, Any]:
        user_text = query.lower().strip()
        
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

        color = None
        for c in ["red", "blue", "green", "yellow", "purple", "pink", "orange", "gold", "silver", "rgb", "black", "white", "gray"]:
            if c in user_text:
                color = c
                break

        gender = None
        if any(w in user_text for w in ["women", "womens", "women's", "female", "lady", "ladies"]):
            gender = "female"
        elif any(w in user_text for w in ["men", "mens", "men's", "male", "gentlemen"]):
            gender = "male"

        size = None
        size_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:inch|\")?', user_text)
        if size_match and size_match.group(1) in ["13.3", "13.6", "14", "15.6", "17.3", "27"]:
            size = size_match.group(1)

        brand = None
        for b in ["lenovo", "apple", "macbook", "thinkpad", "asus", "sony", "razorflow", "proshield", "flowhub", "keycraft", "acoustix", "ultraview", "frostblast", "zenbook", "legion"]:
            if b in user_text:
                brand = b
                break

        features = []
        for feat in ["wireless", "anc", "noise cancelling", "4k", "oled", "mechanical", "water-resistant", "ergonomic", "bluetooth", "144hz", "vertical"]:
            if feat in user_text:
                features.append(feat)

        category = None
        if any(k in user_text for k in ["kurta set", "kurta", "kurtis"]):
            category = "kurta set"
        elif any(k in user_text for k in ["bag", "sleeve", "carry bag", "case", "cover", "pouch"]):
            category = "bag"
        elif any(k in user_text for k in ["mouse", "mice"]):
            category = "mouse"
        elif any(k in user_text for k in ["keyboard", "keycaps"]):
            category = "keyboard"
        elif any(k in user_text for k in ["cooling pad", "cooler"]):
            category = "cooler"
        elif any(k in user_text for k in ["hub", "dongle", "adapter"]):
            category = "hub"
        elif any(k in user_text for k in ["watch", "smartwatch", "timepiece"]):
            category = "watch"
        elif any(k in user_text for k in ["headphone", "headphones", "earphone", "earphones", "headset", "audio", "anc"]):
            category = "audio"
        elif any(k in user_text for k in ["monitor", "monitors", "display", "screen"]):
            category = "monitor"
        elif any(k in user_text for k in ["phone", "smartphone", "mobile", "cellphone"]):
            category = "phone"
        elif any(k in user_text for k in ["laptop", "laptops", "notebook", "macbook", "computer"]):
            category = "laptop"

        return {
            "category": category,
            "attributes": {
                "color": color,
                "gender": gender,
                "size": size,
                "brand": brand,
                "material": None,
                "features": features
            },
            "budget": budget,
            "quantity": 1
        }

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

ai_service = AIService()
