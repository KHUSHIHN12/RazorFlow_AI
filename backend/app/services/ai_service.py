import os
from typing import Dict, Any, List, Optional

class AIService:
    """
    Modular AI Agent Service supporting optional Google Gemini API free-tier model integration
    with seamless fallback to deterministic Product Decision & Ranking Engine.
    """
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "")
        self.use_llm = bool(self.api_key and self.api_key.startswith("AIza"))

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
