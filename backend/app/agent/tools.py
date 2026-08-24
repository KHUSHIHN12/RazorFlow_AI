import json
import os
from typing import List, Dict, Any, Optional
from app.services.razorpay_service import RazorpayService

CATALOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "catalog.json")

STOP_WORDS = {
    "i", "need", "want", "looking", "for", "a", "an", "the", "under", "below",
    "rs", "inr", "show", "me", "find", "best", "good", "great", "top", "also",
    "carry", "only", "please", "can", "you", "my", "this", "that", "it", "with"
}

def load_catalog() -> List[Dict[str, Any]]:
    try:
        with open(CATALOG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as ex:
        print(f"[Tools] Catalog load error: {ex}")
        return []

def search_catalog(query: str = "", max_price: Optional[float] = None, category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Queries product catalog with optional query, max_price, and category filters.
    """
    products = load_catalog()
    results = []
    query_lower = query.lower().strip() if query else ""
    
    for prod in products:
        if category and category.lower() not in prod.get("category", "").lower():
            continue
            
        if max_price is not None and prod.get("price", 0) > max_price:
            continue
            
        if query_lower:
            text_corpus = f"{prod.get('name', '')} {prod.get('description', '')} {' '.join(prod.get('tags', []))}".lower()
            keywords = [k for k in query_lower.split() if k not in STOP_WORDS and len(k) > 1]
            if keywords and not any(kw in text_corpus for kw in keywords):
                continue
                
        results.append(prod)
        
    return results

def getProductDetails(product_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetches full product details by product ID from catalog.
    """
    catalog = load_catalog()
    for prod in catalog:
        if prod["id"] == product_id or prod["name"].lower() == product_id.lower():
            return prod
    return None

def compareProducts(product_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Compares 2 or more products side-by-side using authoritative catalog specs & reviews.
    """
    catalog = load_catalog()
    matched = []
    for pid in product_ids:
        pid_clean = pid.lower().strip()
        for p in catalog:
            if p["id"].lower() == pid_clean or pid_clean in p["name"].lower():
                if p not in matched:
                    matched.append(p)
    return matched

def analyzeReviews(product_id: str) -> Dict[str, Any]:
    """
    Analyzes reviews, rating volume, positive sentiment, and common complaints for a product.
    """
    prod = getProductDetails(product_id)
    if not prod:
        return {"error": "Product not found"}
        
    themes = prod.get("review_themes", {})
    return {
        "product_id": prod["id"],
        "name": prod["name"],
        "rating": prod.get("rating", 4.0),
        "reviews_count": prod.get("reviews_count", 0),
        "positive_themes": themes.get("positive", []),
        "negative_themes": themes.get("negative", []),
        "use_cases": themes.get("use_cases", []),
        "sample_reviews": prod.get("reviews", [])
    }

def manage_cart(cart: List[Dict[str, Any]], action: str, product_id: str, quantity: int = 1) -> Dict[str, Any]:
    """
    Adds, updates, or removes items in the cart and computes total value in currency sub-units (paise) & INR.
    """
    catalog = load_catalog()
    product_map = {p["id"]: p for p in catalog}

    updated_cart = [item.copy() for item in cart]
    
    if action == "add":
        if product_id in product_map:
            prod = product_map[product_id]
            existing = next((i for i in updated_cart if i["product_id"] == product_id), None)
            if existing:
                existing["quantity"] += quantity
            else:
                updated_cart.append({
                    "product_id": prod["id"],
                    "name": prod["name"],
                    "price": float(prod["price"]),
                    "price_paise": int(prod["price_paise"]),
                    "quantity": quantity,
                    "image_url": prod.get("image_url", "")
                })
    elif action == "remove":
        updated_cart = [i for i in updated_cart if i["product_id"] != product_id]
    elif action == "clear":
        updated_cart = []

    total_inr = sum(item["price"] * item["quantity"] for item in updated_cart)
    total_paise = sum(item["price_paise"] * item["quantity"] for item in updated_cart)

    return {
        "cart": updated_cart,
        "total_inr": round(total_inr, 2),
        "total_paise": total_paise,
        "item_count": sum(i["quantity"] for i in updated_cart)
    }

def create_razorpay_order(amount_paise: int, currency: str = "INR") -> Dict[str, Any]:
    """
    Calls the Razorpay API to generate an authentic order_id with currency sub-units.
    """
    return RazorpayService.create_order(amount_paise=amount_paise, currency=currency)
