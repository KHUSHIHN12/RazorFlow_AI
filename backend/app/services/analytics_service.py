from typing import List, Dict, Any, Counter as CounterType
from collections import Counter
import json
import os

CATALOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "catalog.json")

class AnalyticsService:
    def __init__(self):
        # Stateful Event Trackers
        self.category_demand: CounterType[str] = Counter({
            "Laptops": 63,
            "Accessories": 42,
            "Audio": 27,
            "Monitors": 18
        })
        self.search_intents: CounterType[str] = Counter({
            "coding laptops under 60k": 48,
            "noise cancelling headphones": 32,
            "ergonomic mouse for programming": 25,
            "4k developer monitors": 18,
            "macbook m2 deals": 15,
            "usb-c hubs & docking": 12
        })
        self.unfulfilled_queries: CounterType[str] = Counter({
            "Mechanical RGB Keyboards": 14,
            "USB-C Docking Stations": 11,
            "Smartwatches under ₹5k": 9
        })
        self.product_views: CounterType[str] = Counter({
            "ZenBook Pro 14 AI Edition": 74,
            "Acoustix Wireless ANC Pro": 45,
            "UltraView 27\" 4K Developer Monitor": 38,
            "ProShield Laptop Sleeve 14\"": 29,
            "RazorFlow Precision Ergonomic Wireless Mouse": 22
        })
        self.product_orders: CounterType[str] = Counter({
            "ZenBook Pro 14 AI Edition": 28,
            "Acoustix Wireless ANC Pro": 9,
            "RazorFlow Precision Ergonomic Wireless Mouse": 5
        })
        
        self.total_sessions: int = 150
        self.successful_checkouts: int = 42
        self.total_revenue_paise: int = 247800000 # ₹24,78,000

    def _load_catalog(self) -> List[Dict[str, Any]]:
        try:
            with open(CATALOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def log_intent(self, query: str):
        query_clean = query.strip().lower()
        if not query_clean:
            return
        self.search_intents[query_clean[:25]] += 1

    def log_query_analytics(self, query: str, intent: Dict[str, Any], results_count: int, products_returned: List[Dict[str, Any]]):
        self.total_sessions += 1
        query_clean = query.strip().lower()
        if not query_clean:
            return

        cat = intent.get("category")
        if cat:
            cat_normalized = cat.capitalize()
            self.category_demand[cat_normalized] += 1

        # Track search intent keywords
        head_noun = intent.get("head_noun") or query_clean[:25]
        self.search_intents[head_noun] += 1

        # Track product views
        for p in products_returned:
            p_name = p.get("name")
            if p_name:
                self.product_views[p_name] += 1

        # Log unfulfilled requests
        if results_count == 0 or not products_returned:
            self.unfulfilled_queries[query.title()] += 1

    def log_successful_payment(self, amount_paise: int, purchased_items: List[Dict[str, Any]] = None):
        self.successful_checkouts += 1
        self.total_revenue_paise += amount_paise
        if purchased_items:
            for item in purchased_items:
                p_name = item.get("name")
                qty = item.get("quantity", 1)
                if p_name:
                    self.product_orders[p_name] += qty

    def get_metrics(self) -> Dict[str, Any]:
        catalog = self._load_catalog()

        # 1. Key Metrics
        conversion_rate = round((self.successful_checkouts / max(self.total_sessions, 1)) * 100, 1)
        total_revenue_inr = round(self.total_revenue_paise / 100, 2)

        # 2. Customer Demand
        total_searches = sum(self.category_demand.values()) or 1
        categories_demand = []
        for cat_name, count in self.category_demand.most_common(4):
            pct = round((count / total_searches) * 100)
            categories_demand.append({
                "category": cat_name,
                "percentage": pct,
                "search_count": count
            })

        top_intents = [
            {"keyword": kw, "count": count}
            for kw, count in self.search_intents.most_common(5)
        ]

        unfulfilled_requests = []
        for q, count in self.unfulfilled_queries.most_common(3):
            reason = "Out of store catalog" if any(w in q.lower() for w in ["watch", "phone", "kurta", "shirt"]) else "High demand / low stock"
            unfulfilled_requests.append({
                "query": q,
                "count": count,
                "reason": reason
            })

        # 3. Product Performance
        top_products = []
        for prod in catalog:
            p_name = prod["name"]
            orders = self.product_orders.get(p_name, 0)
            if orders > 0:
                price = float(prod.get("price", 0))
                revenue = price * orders
                top_products.append({
                    "name": p_name,
                    "category": prod.get("category", "General"),
                    "price": int(price),
                    "orders": orders,
                    "revenue": int(revenue),
                    "rating": float(prod.get("rating", 4.5))
                })
        top_products.sort(key=lambda x: x["revenue"], reverse=True)

        # High Demand / Low Conversion
        high_demand_low_conversion = []
        for prod in catalog:
            p_name = prod["name"]
            views = self.product_views.get(p_name, 0)
            orders = self.product_orders.get(p_name, 0)
            if views > 15 and (orders / max(views, 1)) < 0.25:
                conv_pct = round((orders / max(views, 1)) * 100, 1)
                high_demand_low_conversion.append({
                    "name": p_name,
                    "price": int(prod.get("price", 0)),
                    "searches": views,
                    "conversion": f"{conv_pct}%",
                    "issue": "Price threshold / friction" if prod.get("price", 0) > 30000 else "Attribute options"
                })

        # 4. Pattern-Driven AI Growth Actions
        ai_growth_actions = self._generate_ai_growth_actions(categories_demand, unfulfilled_requests, high_demand_low_conversion, top_products)

        return {
            "total_sessions": self.total_sessions,
            "successful_checkouts": self.successful_checkouts,
            "conversion_rate": conversion_rate,
            "total_revenue_inr": total_revenue_inr,
            "top_intents": top_intents,
            "categories_demand": categories_demand,
            "unfulfilled_requests": unfulfilled_requests,
            "top_products": top_products[:4],
            "high_demand_low_conversion": high_demand_low_conversion[:2],
            "ai_growth_actions": ai_growth_actions
        }

    def _generate_ai_growth_actions(self, categories_demand, unfulfilled_requests, high_demand_low_conv, top_products) -> List[Dict[str, Any]]:
        from app.services.ai_service import ai_service
        
        aggregated_data = {
            "categories_demand": categories_demand,
            "unfulfilled_requests": unfulfilled_requests,
            "high_demand_low_conversion": high_demand_low_conv,
            "top_products": top_products
        }
        
        return ai_service.generate_growth_recommendations(aggregated_data)

    def launch_campaign(self, campaign_id: str) -> Dict[str, Any]:
        return {"status": "success"}

analytics_service = AnalyticsService()
