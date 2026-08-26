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

analytics_service = AnalyticsService()
