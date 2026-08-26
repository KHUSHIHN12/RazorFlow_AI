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

    @classmethod
    def parse_intent(cls, query: str, max_price: Optional[float] = None) -> Dict[str, Any]:
        from app.services.ai_service import ai_service
        
        user_text = query.lower().strip()
        structured_raw = ai_service.extract_structured_intent(query)

        raw_cat = structured_raw.get("category")
        attrs = structured_raw.get("attributes", {})
        budget = structured_raw.get("budget") or max_price

        # Robust budget fallback if missing from structured JSON
        if budget is None:
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

        # Focus area detection
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

        # Attribute extraction from structured LLM/Deterministic result
        color = attrs.get("color")
        gender = attrs.get("gender")
        size = attrs.get("size")
        brand = attrs.get("brand")
        req_features = attrs.get("features", [])

        # Fallback text regex for attributes if LLM returned null
        if not color:
            for c in ["red", "blue", "green", "yellow", "purple", "pink", "orange", "gold", "silver", "rgb", "black", "white", "gray"]:
                if c in user_text:
                    color = c
                    break

        if not gender:
            if any(w in user_text for w in ["women", "womens", "women's", "female", "lady", "ladies"]):
                gender = "female"
            elif any(w in user_text for w in ["men", "mens", "men's", "male", "gentlemen"]):
                gender = "male"

        if not size:
            size_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:inch|\")?', user_text)
            if size_match and size_match.group(1) in ["13.3", "13.6", "14", "15.6", "17.3", "27"]:
                size = size_match.group(1)

        if not brand:
            for b in ["lenovo", "apple", "macbook", "thinkpad", "asus", "sony", "razorflow", "proshield", "flowhub", "keycraft", "acoustix", "ultraview", "frostblast", "zenbook", "legion"]:
                if b in user_text:
                    brand = b
                    break

        # Category and Head Noun resolution
        category = None
        head_noun = None

        if raw_cat:
            r_cat = str(raw_cat).lower().strip()
            if any(k in r_cat for k in ["kurta set", "kurta", "kurtis"]):
                category = "kurta set"
                head_noun = "kurta set"
            elif any(k in r_cat for k in ["bag", "sleeve", "carry bag", "case", "pouch"]):
                category = "Accessories"
                head_noun = "bag"
            elif "mouse" in r_cat or "mice" in r_cat:
                category = "Accessories"
                head_noun = "mouse"
            elif "keyboard" in r_cat:
                category = "Accessories"
                head_noun = "keyboard"
            elif "cooler" in r_cat or "cooling" in r_cat:
                category = "Accessories"
                head_noun = "cooler"
            elif "hub" in r_cat or "adapter" in r_cat:
                category = "Accessories"
                head_noun = "hub"
            elif "watch" in r_cat or "smartwatch" in r_cat:
                category = "Watches"
                head_noun = "watch"
            elif any(k in r_cat for k in ["headphone", "audio", "earphone", "headset"]):
                category = "Audio"
                head_noun = "audio"
            elif "monitor" in r_cat or "display" in r_cat:
                category = "Monitors"
                head_noun = "monitor"
            elif "phone" in r_cat or "mobile" in r_cat:
                category = "Phones"
                head_noun = "phone"
            elif "laptop" in r_cat or "macbook" in r_cat or "computer" in r_cat:
                category = "Laptops"
                head_noun = "laptop"
            else:
                category = raw_cat
                head_noun = raw_cat

        # Secondary fallback for category if raw_cat was None
        if not category:
            if any(k in user_text for k in ["kurta set", "kurta", "kurtis"]):
                category = "kurta set"
                head_noun = "kurta set"
            elif any(k in user_text for k in ["bag", "sleeve", "carry bag", "case", "cover", "pouch"]):
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
            elif any(k in user_text for k in ["headphone", "headphones", "earphone", "earphones", "headset", "audio", "anc"]):
                category = "Audio"
                head_noun = "audio"
            elif any(k in user_text for k in ["monitor", "monitors", "display", "screen"]):
                category = "Monitors"
                head_noun = "monitor"
            elif any(k in user_text for k in ["phone", "smartphone", "mobile", "cellphone"]):
                category = "Phones"
                head_noun = "phone"
            elif any(k in user_text for k in ["laptop", "laptops", "notebook", "macbook", "computer"]):
                category = "Laptops"
                head_noun = "laptop"

        return {
            "query": user_text,
            "max_price": budget,
            "focus_area": focus_area,
            "category": category,
            "head_noun": head_noun,
            "brand": brand,
            "color": color,
            "gender": gender,
            "size": size,
            "material": attrs.get("material"),
            "style": attrs.get("style"),
            "use_case": attrs.get("use_case"),
            "required_features": req_features,
            "structured_intent": structured_raw
        }

    @classmethod
    def filter_candidates_by_intent(cls, catalog: List[Dict[str, Any]], intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes strict multi-stage constraint filtering with fallback priority:
        Priority 1: Product/category (PRIMARY - NEVER relaxed before attributes!)
        Priority 2: Explicit user attributes (brand, color, size, material, features)
        Priority 3: Budget fit
        Priority 4: Availability
        Priority 5: Specifications
        Priority 6: Rating/reviews
        """
        cat = intent.get("category")
        head_n = intent.get("head_noun")
        max_p = intent.get("max_price")
        brand = intent.get("brand")
        color = intent.get("color")
        size = intent.get("size")
        material = intent.get("material")
        req_features = intent.get("required_features", [])

        # Stage 1: Strict Mandatory Category & Head Noun Product Isolation
        stage1_candidates = []
        for prod in catalog:
            prod_cat = prod.get("category", "").lower()
            prod_name = prod.get("name", "").lower()
            prod_desc = prod.get("description", "").lower()
            prod_tags = [t.lower() for t in prod.get("tags", [])]
            prod_corpus = f"{prod_name} {prod_desc} {' '.join(prod_tags)}"

            if head_n:
                hn = head_n.lower().strip()
                hn_matches = False
                if hn in ["laptop", "notebook", "macbook"]:
                    if prod_cat == "laptops" or any(l in prod_name for l in ["zenbook", "thinkpad", "macbook", "legion"]):
                        if not any(acc in prod_name for acc in ["sleeve", "bag", "cooling pad", "cooler", "hub", "mouse", "keyboard"]):
                            hn_matches = True
                elif hn in ["bag", "sleeve", "case", "pouch", "backpack"]:
                    if prod_cat == "accessories" and any(b in prod_name or b in prod_corpus for b in ["bag", "sleeve", "case", "pouch", "backpack"]):
                        hn_matches = True
                elif hn in ["mouse", "mice"]:
                    if prod_cat == "accessories" and any(m in prod_name or m in prod_corpus for m in ["mouse", "mice"]):
                        hn_matches = True
                elif hn in ["keyboard", "keycaps"]:
                    if prod_cat == "accessories" and ("keyboard" in prod_name or "keycaps" in prod_name):
                        hn_matches = True
                elif hn in ["cooler", "cooling"]:
                    if prod_cat == "accessories" and ("cooler" in prod_name or "cooling" in prod_name or "cooling pad" in prod_corpus):
                        hn_matches = True
                elif hn in ["hub", "dongle", "adapter"]:
                    if prod_cat == "accessories" and ("hub" in prod_name or "dongle" in prod_name or "adapter" in prod_name):
                        hn_matches = True
                elif hn in ["audio", "headphone", "headphones", "headset", "earphone", "earbuds"]:
                    if prod_cat == "audio" or any(a in prod_name for a in ["headphone", "headphones", "headset", "earphone", "earbuds", "acoustix", "anc"]):
                        hn_matches = True
                elif hn in ["monitor", "display", "screen"]:
                    if prod_cat == "monitors" or any(m in prod_name for m in ["monitor", "display", "screen"]):
                        hn_matches = True
                else:
                    hn_matches = (hn in prod_name or hn in prod_desc or any(hn in tag for tag in prod_tags))

                if not hn_matches:
                    continue

            if cat:
                c_clean = cat.lower().strip()
                if c_clean in ["laptops", "audio", "monitors", "accessories"]:
                    if prod_cat != c_clean:
                        continue
                else:
                    if c_clean not in prod_cat and c_clean not in prod_corpus:
                        continue

            stage1_candidates.append(prod)

        if not stage1_candidates:
            return {
                "fallback_level": "no_category",
                "exact_matches": [],
                "relaxed_attribute_matches": [],
                "relaxed_budget_matches": [],
                "category_exists": False,
                "stage1_candidates": []
            }

        # Evaluate attributes and budget for items strictly within requested category
        exact_matches = []
        relaxed_attribute_matches = [] # Fits budget, missing 1+ optional attributes
        relaxed_budget_matches = []    # Exceeds budget in same category

        for prod in stage1_candidates:
            prod_corpus = f"{prod.get('name', '')} {prod.get('description', '')} {' '.join(prod.get('tags', []))} {str(prod.get('specs', {}))}".lower()
            
            missing_attrs = []
            if brand and not re.search(r'\b' + re.escape(brand) + r'\b', prod_corpus):
                missing_attrs.append(f"brand '{brand}'")
            if color and not re.search(r'\b' + re.escape(color) + r'\b', prod_corpus):
                missing_attrs.append(f"color '{color}'")
            if size and not re.search(r'\b' + re.escape(size) + r'\b', prod_corpus):
                missing_attrs.append(f"size '{size}'")
            if material and not re.search(r'\b' + re.escape(material) + r'\b', prod_corpus):
                missing_attrs.append(f"material '{material}'")
            
            for feat in req_features:
                if not re.search(r'\b' + re.escape(feat) + r'\b', prod_corpus):
                    missing_attrs.append(f"feature '{feat}'")

            price = float(prod.get("price", 0))
            budget_exceeded = (max_p is not None) and (price > max_p)

            if not missing_attrs and not budget_exceeded:
                exact_matches.append(prod)
            elif missing_attrs and not budget_exceeded:
                relaxed_attribute_matches.append((prod, missing_attrs))
            elif budget_exceeded:
                relaxed_budget_matches.append((prod, missing_attrs))

        min_cat_price = min(float(p.get("price", 0)) for p in stage1_candidates) if stage1_candidates else 0
        price_delta = (min_cat_price - max_p) if (max_p is not None and min_cat_price > max_p) else 0

        # Collect unique missing attribute labels
        all_missing_attrs = []
        for prod in stage1_candidates:
            prod_corpus = f"{prod.get('name', '')} {prod.get('description', '')} {' '.join(prod.get('tags', []))} {str(prod.get('specs', {}))}".lower()
            if brand and brand not in prod_corpus and f"brand '{brand}'" not in all_missing_attrs:
                all_missing_attrs.append(f"brand '{brand}'")
            if color and color not in prod_corpus and f"color '{color}'" not in all_missing_attrs:
                all_missing_attrs.append(f"color '{color}'")
            if size and size not in prod_corpus and f"size '{size}'" not in all_missing_attrs:
                all_missing_attrs.append(f"size '{size}'")
            if material and material not in prod_corpus and f"material '{material}'" not in all_missing_attrs:
                all_missing_attrs.append(f"material '{material}'")
            for feat in req_features:
                if feat not in prod_corpus and f"feature '{feat}'" not in all_missing_attrs:
                    all_missing_attrs.append(f"feature '{feat}'")

        has_attr_conflict = bool(all_missing_attrs)
        has_budget_conflict = (price_delta > 0) or bool(relaxed_budget_matches)

        if exact_matches:
            fallback_level = "exact_match"
            conflict_type = "none"
        elif has_attr_conflict and has_budget_conflict:
            # Both attribute and budget constraints failed
            fallback_level = "multi_constraint"
            conflict_type = "multi_constraint"
        elif has_attr_conflict:
            fallback_level = "relaxed_attributes"
            conflict_type = "attributes_only"
        elif has_budget_conflict:
            fallback_level = "relaxed_budget"
            conflict_type = "budget_only"
        else:
            fallback_level = "no_category"
            conflict_type = "no_category"

        return {
            "fallback_level": fallback_level,
            "conflict_type": conflict_type,
            "exact_matches": exact_matches,
            "relaxed_attribute_matches": relaxed_attribute_matches,
            "relaxed_budget_matches": relaxed_budget_matches,
            "category_exists": True,
            "stage1_candidates": stage1_candidates,
            "min_category_price": min_cat_price,
            "price_delta": price_delta,
            "missing_attributes": all_missing_attrs
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
        
        spec_parts = [f"{k.replace('_', ' ').title()}: {v}" for k, v in specs.items() if v]
        if spec_parts:
            spec_bullet = f"• Key specs: {', '.join(spec_parts[:3])}"
        else:
            spec_bullet = f"• Features: {prod.get('description', '')[:70]}..."

        explanation = (
            f"Why I recommend it:\n"
            f"• Fits your budget (₹{price:,.0f})\n"
            f"{spec_bullet}\n"
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
    def rank_alternative_candidates(cls, candidates: List[Dict[str, Any]], intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Ranks same-category alternatives using priority order:
        Category match (mandatory) -> remaining requested attributes -> budget fit -> rating/reviews -> specs -> relevance.
        """
        if not candidates:
            return []

        brand = intent.get("brand")
        color = intent.get("color")
        size = intent.get("size")
        req_features = intent.get("required_features", [])
        max_p = intent.get("max_price")

        total_req_attrs = (1 if brand else 0) + (1 if color else 0) + (1 if size else 0) + len(req_features)

        scored = []
        for prod in candidates:
            prod_corpus = f"{prod.get('name', '')} {prod.get('description', '')} {' '.join(prod.get('tags', []))} {str(prod.get('specs', {}))}".lower()
            
            matched_count = 0
            missing_attrs = []
            matched_attrs = []

            if brand:
                if re.search(r'\b' + re.escape(brand) + r'\b', prod_corpus):
                    matched_count += 1
                    matched_attrs.append(f"brand '{brand}'")
                else:
                    missing_attrs.append(f"brand '{brand}'")

            if color:
                if re.search(r'\b' + re.escape(color) + r'\b', prod_corpus):
                    matched_count += 1
                    matched_attrs.append(f"color '{color}'")
                else:
                    missing_attrs.append(f"color '{color}'")

            if size:
                if re.search(r'\b' + re.escape(size) + r'\b', prod_corpus):
                    matched_count += 1
                    matched_attrs.append(f"size '{size}'")
                else:
                    missing_attrs.append(f"size '{size}'")

            for feat in req_features:
                if re.search(r'\b' + re.escape(feat) + r'\b', prod_corpus):
                    matched_count += 1
                    matched_attrs.append(f"feature '{feat}'")
                else:
                    missing_attrs.append(f"feature '{feat}'")

            attr_ratio_score = (matched_count / total_req_attrs * 100.0) if total_req_attrs > 0 else 80.0

            price = float(prod.get("price", 0))
            if max_p:
                if price <= max_p:
                    budget_score = 100.0
                else:
                    exceed_ratio = (price - max_p) / max_p
                    budget_score = max(0.0, 100.0 - (exceed_ratio * 200.0))
            else:
                budget_score = 80.0

            raw_rating = float(prod.get("rating", 4.0))
            rev_count = int(prod.get("reviews_count", 10))
            bayesian_val = cls.calculate_bayesian_rating(raw_rating, rev_count)
            bayesian_score = max(0.0, min(100.0, (bayesian_val - 3.5) / (5.0 - 3.5) * 100.0))

            spec_score = 70.0
            if "16gb" in prod_corpus or "4k" in prod_corpus or "oled" in prod_corpus or "wireless" in prod_corpus:
                spec_score += 15.0

            composite_alt_score = (
                (attr_ratio_score * 0.40) +
                (budget_score * 0.25) +
                (bayesian_score * 0.20) +
                (spec_score * 0.15)
            )

            scored.append({
                "product": prod,
                "score": round(composite_alt_score, 1),
                "missing_attrs": missing_attrs,
                "matched_attrs": matched_attrs
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    @classmethod
    def find_closest_above_budget(cls, candidates: List[Dict[str, Any]], max_price: float) -> Optional[Dict[str, Any]]:
        above_budget = [p for p in candidates if float(p.get("price", 0)) > max_price]
        if not above_budget:
            return None
        above_budget.sort(key=lambda p: float(p.get("price", 0)))
        return above_budget[0]

ranking_engine = ProductDecisionEngine()
