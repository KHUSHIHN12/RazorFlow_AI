from typing import List, Dict, Any, Counter as CounterType
from collections import Counter
import datetime

class AnalyticsService:
    def __init__(self):
        self.intents: CounterType[str] = Counter({
            "coding laptops under 60k": 48,
            "noise cancelling headphones": 32,
            "ergonomic mouse for programming": 25,
            "4k developer monitors": 18,
            "macbook m2 deals": 15,
            "usb-c hubs & docking": 12
        })
        self.total_sessions: int = 150
        self.successful_checkouts: int = 42
        self.total_revenue_paise: int = 247800000 # ~₹24,78,000
        self.campaigns: List[Dict[str, Any]] = [
            {
                "id": "camp_01",
                "title": "Ultimate Coder Starter Kit",
                "bundle_items": ["ZenBook Pro 14", "Ergonomic Mouse", "7-in-1 USB-C Hub"],
                "discount_percent": 12,
                "projected_conversion_lift": "+18.5%",
                "status": "Active",
                "created_at": "2026-08-20"
            },
            {
                "id": "camp_02",
                "title": "Quiet Workspace Audio + Monitor Bundle",
                "bundle_items": ["Acoustix ANC Pro", "UltraView 27\" 4K Monitor"],
                "discount_percent": 15,
                "projected_conversion_lift": "+22.1%",
                "status": "AI Recommended",
                "created_at": "2026-08-22"
            }
        ]

    def log_intent(self, query: str):
        query_clean = query.strip().lower()
        if not query_clean:
            return
        
        # Categorize query into top intent categories
        if "laptop" in query_clean or "coding" in query_clean or "under" in query_clean:
            self.intents["coding laptops under 60k"] += 1
        elif "headphone" in query_clean or "audio" in query_clean or "noise" in query_clean:
            self.intents["noise cancelling headphones"] += 1
        elif "mouse" in query_clean or "ergonomic" in query_clean:
            self.intents["ergonomic mouse for programming"] += 1
        elif "monitor" in query_clean or "display" in query_clean or "4k" in query_clean:
            self.intents["4k developer monitors"] += 1
        elif "macbook" in query_clean or "apple" in query_clean:
            self.intents["macbook m2 deals"] += 1
        else:
            self.intents[query_clean[:30]] += 1
        
        self.total_sessions += 1

    def log_successful_payment(self, amount_paise: int):
        self.successful_checkouts += 1
        self.total_revenue_paise += amount_paise

    def get_metrics(self) -> Dict[str, Any]:
        conversion_rate = round((self.successful_checkouts / max(self.total_sessions, 1)) * 100, 1)
        
        top_intents = [
            {"keyword": kw, "count": count}
            for kw, count in self.intents.most_common(6)
        ]

        categories_demand = [
            {"category": "Laptops", "percentage": 42, "search_count": 63},
            {"category": "Accessories", "percentage": 28, "search_count": 42},
            {"category": "Audio", "percentage": 18, "search_count": 27},
            {"category": "Monitors", "percentage": 12, "search_count": 18}
        ]

        unfulfilled_requests = [
            {"query": "Mechanical RGB Keyboards", "count": 14, "reason": "Low stock"},
            {"query": "USB-C Docking Stations", "count": 11, "reason": "Missing catalog item"},
            {"query": "Smartwatches under ₹5k", "count": 9, "reason": "Category out of catalog"}
        ]

        top_products = [
            {"name": "ZenBook Pro 14 AI Edition", "category": "Laptops", "price": 58999, "orders": 28, "revenue": 1651972, "rating": 4.8},
            {"name": "Acoustix Wireless ANC Pro", "category": "Audio", "price": 14999, "orders": 9, "revenue": 134991, "rating": 4.8},
            {"name": "RazorFlow Ergonomic Mouse", "category": "Accessories", "price": 2499, "orders": 5, "revenue": 12495, "rating": 4.6}
        ]

        high_demand_low_conversion = [
            {"name": "UltraView 27\" 4K Developer Monitor", "price": 32999, "searches": 38, "conversion": "5.2%", "issue": "Price threshold"},
            {"name": "ProShield Laptop Sleeve 14\"", "price": 1299, "searches": 29, "conversion": "8.1%", "issue": "Color options"}
        ]

        ai_growth_actions = [
            {
                "id": "act_1",
                "insight": "High demand for coding laptops under ₹60K",
                "action": "Promote top-rated ZenBook Pro 14 AI Edition in agent recommendations",
                "impact": "+18.5% conversion opportunity"
            },
            {
                "id": "act_2",
                "insight": "Frequent unfulfilled searches for mechanical keyboards and USB-C hubs",
                "action": "Stock KeyCraft Mechanical Keyboard & FlowHub 7-in-1 USB-C Hub",
                "impact": "+14.2% catalog coverage & revenue lift"
            },
            {
                "id": "act_3",
                "insight": "Strong 4.8★ rating for Acoustix ANC Headphones",
                "action": "Launch 'Quiet Workspace' Audio + Monitor bundle with 12% promotional discount",
                "impact": "+22.1% cross-sell basket size"
            }
        ]
        
        return {
            "total_sessions": self.total_sessions,
            "successful_checkouts": self.successful_checkouts,
            "conversion_rate": conversion_rate,
            "total_revenue_inr": round(self.total_revenue_paise / 100, 2),
            "top_intents": top_intents,
            "categories_demand": categories_demand,
            "unfulfilled_requests": unfulfilled_requests,
            "top_products": top_products,
            "high_demand_low_conversion": high_demand_low_conversion,
            "ai_growth_actions": ai_growth_actions,
            "campaigns": self.campaigns
        }

    def launch_campaign(self, campaign_id: str) -> Dict[str, Any]:
        for camp in self.campaigns:
            if camp["id"] == campaign_id:
                camp["status"] = "Active"
                return camp
        return {}

analytics_service = AnalyticsService()
