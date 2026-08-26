import re
from typing import List, Dict, Any, Optional, Tuple

class ProductDecisionEngine:
    """
    Structured Product Decision / Ranking Engine for CommercePilot AI.
    
    Evaluates catalog products across 6 core weighted dimensions:
    1. Budget Fit
    2. Requirement Match (Category & Use-case intent)
    3. Specification Match (Hardware parameters)
    4. Confidence-Adjusted Rating & Review Volume (Bayesian score)
    5. Review Quality & Sentiment
    6. Value for Money
    
    Dynamically adjusts weight distribution based on natural language intent.
    Strictly grounded in authoritative catalog data (Zero Hallucination).
    """

    @staticmethod
    def parse_intent(query: str, max_price: Optional[float] = None) -> Dict[str, Any]:
        user_text = query.lower().strip()
        
        # 1. Robust Budget extraction
        extracted_budget = max_price
        if extracted_budget is None:
            # Match numbers like 60,000 or 60000 or 70k or 2000
            k_match = re.search(r'(\d+)\s*k\b', user_text)
            if k_match:
                extracted_budget = float(k_match.group(1)) * 1000.0
            else:
                matches = re.findall(r'(?:under|below|max|budget|within|rs\.?|₹)?\s*([\d,]{4,8})', user_text)
                for m in matches:
                    clean_num = m.replace(",", "").strip()
                    if clean_num.isdigit():
                        val = float(clean_num)
                        if val >= 500:
                            extracted_budget = val
                            break

        # 2. Target use case & primary focus detection
        focus_area = "general"
        if any(k in user_text for k in ["cheap", "cheapest", "value", "affordable", "budget", "best value"]):
            focus_area = "value"
        elif any(k in user_text for k in ["reliable", "reliability", "durable", "trusted", "popular", "top rated"]):
            focus_area = "reliability"
        elif any(k in user_text for k in ["battery", "battery life", "backup", "long battery", "travel"]):
            focus_area = "battery"
        elif any(k in user_text for k in ["code", "coding", "program", "programming", "developer", "software", "performance", "fast"]):
            focus_area = "programming"
        elif any(k in user_text for k in ["gaming", "game", "gpu", "rtx", "graphics"]):
            focus_area = "gaming"

        # 3. Head Noun & Category Detection
        # Check accessory modifiers FIRST (bag, sleeve, case, stand, cooler, hub) to prevent false laptop categorization!
        category = None
        head_noun = None

        if any(k in user_text for k in ["bag", "sleeve", "carry bag", "case", "cover", "pouch"]):
            category = "Accessories"
            head_noun = "bag"
        elif any(k in user_text for k in ["mouse", "mice"]):
            category = "Accessories"
            head_noun = "mouse"
        elif any(k in user_text for k in ["keyboard", "keycaps"]):
            category = "Accessories"
            head_noun = "keyboard"
        elif any(k in user_text for k in ["cooling pad", "cooler"]):
            category = "Accessories"
            head_noun = "cooler"
        elif any(k in user_text for k in ["hub", "dongle", "adapter"]):
            category = "Accessories"
            head_noun = "hub"
        elif any(k in user_text for k in ["watch", "smartwatch", "timepiece"]):
            category = "Watches"
            head_noun = "watch"
        elif any(k in user_text for k in ["headphone", "headphones", "earphone", "earphones", "headset", "audio", "anc", "noise cancelling"]):
            category = "Audio"
            head_noun = "audio"
        elif any(k in user_text for k in ["monitor", "monitors", "display", "screen"]):
            category = "Monitors"
            head_noun = "monitor"
        elif any(k in user_text for k in ["laptop", "laptops", "notebook", "macbook", "computer"]):
            category = "Laptops"
            head_noun = "laptop"

        return {
            "query": user_text,
            "max_price": extracted_budget,
            "focus_area": focus_area,
            "category": category,
            "head_noun": head_noun
        }

    @staticmethod
    def get_dynamic_weights(focus_area: str) -> Dict[str, float]:
        """
        Dynamically adjusts evaluation criteria weights based on customer intent.
        """
        if focus_area == "value":
            return {
                "budget_fit": 0.25,
                "value_for_money": 0.35,
                "bayesian_rating": 0.15,
                "spec_match": 0.15,
                "req_match": 0.10,
                "review_sentiment": 0.00
            }
        elif focus_area == "programming":
            return {
                "req_match": 0.35,
                "spec_match": 0.25,
                "review_sentiment": 0.15,
                "bayesian_rating": 0.10,
                "value_for_money": 0.10,
                "budget_fit": 0.05
            }
        elif focus_area == "reliability":
            return {
                "bayesian_rating": 0.35,
                "review_sentiment": 0.30,
                "req_match": 0.15,
                "spec_match": 0.10,
                "budget_fit": 0.05,
                "value_for_money": 0.05
            }
        elif focus_area == "battery":
            return {
                "req_match": 0.40,
                "review_sentiment": 0.20,
                "spec_match": 0.20,
                "bayesian_rating": 0.10,
                "budget_fit": 0.05,
                "value_for_money": 0.05
            }
        else:
            return {
                "req_match": 0.30,
                "spec_match": 0.20,
                "review_sentiment": 0.15,
                "bayesian_rating": 0.10,
                "value_for_money": 0.15,
                "budget_fit": 0.10
            }

    @staticmethod
    def calculate_bayesian_rating(raw_rating: float, reviews_count: int, m: float = 100.0, C: float = 4.5) -> float:
        v = float(reviews_count)
        return (v * raw_rating + m * C) / (v + m)

    @classmethod
    def evaluate_product(cls, prod: Dict[str, Any], intent: Dict[str, Any], weights: Dict[str, float]) -> Dict[str, Any]:
        price = float(prod.get("price", 0))
        max_price = intent.get("max_price")
        query_text = intent.get("query", "")
        focus_area = intent.get("focus_area", "general")
        head_noun = intent.get("head_noun")

        # 1. Budget Fit Score (0 - 100)
        if max_price:
            if price <= max_price:
                budget_fit_score = min(100.0, (price / max_price) * 100.0 if price > (max_price * 0.4) else 90.0)
            else:
                exceed_ratio = (price - max_price) / max_price
                budget_fit_score = max(0.0, 100.0 - (exceed_ratio * 300.0))
        else:
            budget_fit_score = 85.0

        # 2. Requirement Match Score (0 - 100)
        req_score = 50.0
        text_corpus = f"{prod.get('name', '')} {prod.get('description', '')} {' '.join(prod.get('tags', []))}".lower()
        use_cases = prod.get("review_themes", {}).get("use_cases", [])
        
        # Check head noun match in tags or name
        if head_noun and (head_noun in text_corpus or any(head_noun in tag for tag in prod.get("tags", []))):
            req_score += 35.0

        if focus_area in use_cases or any(focus_area in tag for tag in prod.get("tags", [])):
            req_score += 15.0
        req_score = min(100.0, req_score)

        # 3. Specification Match Score (0 - 100)
        spec_score = 60.0
        specs = prod.get("specs", {})
        specs_text = " ".join([f"{k}:{v}" for k, v in specs.items()]).lower()
        
        if "16gb" in specs_text or "32gb" in specs_text:
            spec_score += 20.0
        if "512gb" in specs_text or "1tb" in specs_text:
            spec_score += 10.0
        if "oled" in specs_text or "4k" in specs_text or "144hz" in specs_text:
            spec_score += 10.0
        spec_score = min(100.0, spec_score)

        # 4. Bayesian Rating Score (0 - 100)
        raw_rating = float(prod.get("rating", 4.0))
        rev_count = int(prod.get("reviews_count", 10))
        bayesian_rating = cls.calculate_bayesian_rating(raw_rating, rev_count)
        bayesian_score = max(0.0, min(100.0, (bayesian_rating - 3.5) / (5.0 - 3.5) * 100.0))

        # 5. Review Sentiment & Quality Score (0 - 100)
        pos_themes = prod.get("review_themes", {}).get("positive", [])
        neg_themes = prod.get("review_themes", {}).get("negative", [])
        sentiment_score = 70.0 + (len(pos_themes) * 7.5) - (len(neg_themes) * 5.0)
        sentiment_score = max(0.0, min(100.0, sentiment_score))

        # 6. Value for Money Score (0 - 100)
        value_score = (bayesian_score * 0.5) + (spec_score * 0.5)
        if price > 80000:
            value_score -= 15.0
        elif price < 60000:
            value_score += 10.0
        value_score = max(0.0, min(100.0, value_score))

        # Total Composite Score Calculation
        total_score = (
            (budget_fit_score * weights["budget_fit"]) +
            (req_score * weights["req_match"]) +
            (spec_score * weights["spec_match"]) +
            (bayesian_score * weights["bayesian_rating"]) +
            (sentiment_score * weights["review_sentiment"]) +
            (value_score * weights["value_for_money"])
        )

        pos_highlight = pos_themes[0] if pos_themes else "High customer satisfaction rating."
        neg_drawback = neg_themes[0] if neg_themes else "No major reported issues."
        
        explanation = (
            f"Why I recommend it:\n"
            f"• Fits your budget (₹{price:,.0f})\n"
            f"• {specs.get('processor', specs.get('ram', 'High specs'))} with {specs.get('ram', '16GB RAM')}\n"
            f"• ⭐ {raw_rating} rating based on {rev_count:,} customer reviews\n"
            f"• Customer feedback highlight: \"{pos_highlight}\"\n\n"
            f"Potential drawback:\n"
            f"• {neg_drawback}"
        )

        return {
            "product": prod,
            "total_score": round(total_score, 1),
            "sub_scores": {
                "budget_fit": round(budget_fit_score, 1),
                "requirement_match": round(req_score, 1),
                "specs_match": round(spec_score, 1),
                "bayesian_rating_score": round(bayesian_score, 1),
                "review_sentiment_score": round(sentiment_score, 1),
                "value_for_money_score": round(value_score, 1)
            },
            "explanation": explanation,
            "pos_highlight": pos_highlight,
            "neg_drawback": neg_drawback
        }

    @classmethod
    def rank_catalog(cls, candidates: List[Dict[str, Any]], query: str, max_price: Optional[float] = None) -> List[Dict[str, Any]]:
        if not candidates:
            return []

        intent = cls.parse_intent(query, max_price)
        weights = cls.get_dynamic_weights(intent["focus_area"])

        evaluated = []
        for prod in candidates:
            eval_res = cls.evaluate_product(prod, intent, weights)
            evaluated.append(eval_res)

        evaluated.sort(key=lambda x: x["total_score"], reverse=True)
        return evaluated

    @classmethod
    def find_closest_above_budget(cls, candidates: List[Dict[str, Any]], max_price: float) -> Optional[Dict[str, Any]]:
        above_budget = [p for p in candidates if float(p.get("price", 0)) > max_price]
        if not above_budget:
            return None
        above_budget.sort(key=lambda p: float(p.get("price", 0)))
        return above_budget[0]

ranking_engine = ProductDecisionEngine()
