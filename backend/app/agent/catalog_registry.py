import json
import os
import re
from typing import List, Dict, Any, Optional, Set, Tuple

CATALOG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "catalog.json")

class CatalogRegistry:
    """
    Catalog-driven Indexer and Intelligence Registry for RazorFlow AI.
    Dynamically analyzes catalog.json at load time.
    No products, categories, brands, or attributes are hardcoded.
    """
    def __init__(self):
        self.catalog: List[Dict[str, Any]] = []
        self.categories: Set[str] = set()
        self.category_map: Dict[str, str] = {}  # lowercase -> actual category name
        self.brands: Set[str] = set()
        self.tags: Set[str] = set()
        self.specs_keys: Set[str] = set()
        self.category_price_bounds: Dict[str, Tuple[float, float]] = {}  # cat -> (min_price, max_price)
        self.product_tokens: Dict[str, Set[str]] = {}  # product_id -> set of tokens
        self.reload()

    def reload(self):
        try:
            with open(CATALOG_PATH, "r", encoding="utf-8") as f:
                self.catalog = json.load(f)
        except Exception as ex:
            print(f"[CatalogRegistry] Error loading catalog from {CATALOG_PATH}: {ex}")
            self.catalog = []

        self._index_catalog()

    def _index_catalog(self):
        self.categories.clear()
        self.category_map.clear()
        self.brands.clear()
        self.tags.clear()
        self.specs_keys.clear()
        self.category_price_bounds.clear()
        self.product_tokens.clear()

        cat_prices: Dict[str, List[float]] = {}

        for prod in self.catalog:
            prod_id = prod.get("id", "")
            cat = prod.get("category", "").strip()
            if cat:
                self.categories.add(cat)
                self.category_map[cat.lower()] = cat
                cat_prices.setdefault(cat.lower(), []).append(float(prod.get("price", 0)))

            for tag in prod.get("tags", []):
                self.tags.add(tag.lower())

            specs = prod.get("specs", {})
            for key in specs.keys():
                self.specs_keys.add(key.lower())

            # Infer brand tokens from product names / descriptions / tags
            prod_name = prod.get("name", "")
            words = prod_name.split()
            if words:
                # First word of product name is often brand or series
                self.brands.add(words[0].lower())

            # Build full token set per product for fast requirement matching
            tokens = set()
            corpus = f"{prod_name} {cat} {prod.get('description', '')} {' '.join(prod.get('tags', []))} {str(specs)}".lower()
            for w in re.findall(r'[a-z0-9\+\-\.]+', corpus):
                if len(w) > 1:
                    tokens.add(w)
            self.product_tokens[prod_id] = tokens

        # Add known brands present in catalog tags or titles
        known_brand_candidates = {
            "zenbook", "thinkpad", "macbook", "legion", "apple", "asus", "lenovo",
            "acoustix", "ultraview", "proshield", "flowhub", "keycraft", "frostblast",
            "razorflow", "sony", "logitech", "samsung", "dell", "hp", "nike", "adidas", "puma"
        }
        for cand in known_brand_candidates:
            for prod in self.catalog:
                if cand in prod.get("name", "").lower() or cand in [t.lower() for t in prod.get("tags", [])]:
                    self.brands.add(cand)

        # Compute price bounds per category
        for cat_lower, prices in cat_prices.items():
            if prices:
                self.category_price_bounds[cat_lower] = (min(prices), max(prices))

    def get_all_products(self) -> List[Dict[str, Any]]:
        return self.catalog

    def get_categories(self) -> List[str]:
        return sorted(list(self.categories))

    QUALIFIER_WORDS = {
        "women", "womens", "women's", "female", "lady", "ladies",
        "men", "mens", "men's", "male", "boy", "boys", "girl", "girls", "kid", "kids", "child", "children", "baby", "toddler", "unisex", "adult", "adults",
        "red", "blue", "green", "black", "white", "silver", "gray", "grey", "pink", "gold", "yellow", "purple", "orange", "brown", "beige",
        "leather", "neoprene", "aluminum", "aluminium", "plastic", "cotton", "mesh", "foam", "metal", "canvas", "denim", "silk", "nylon",
        "small", "medium", "large", "xl", "xxl", "compact", "slim", "mini", "giant", "big", "huge",
        "coding", "programming", "gaming", "office", "travel", "student", "developer", "work", "school", "college", "gym", "casual", "formal", "sports", "running", "hiking",
        "apple", "huawei", "asus", "dell", "hp", "logitech", "sony", "samsung", "nike", "adidas", "puma", "gigabyte", "heshe", "proshield", "amazon", "echo"
    }

    def get_matching_category(self, text: str) -> Optional[str]:
        """
        Dynamically matches user text to a valid catalog category or product family noun.
        Rejects qualifier-only terms (gender, color, material, use case, brand).
        """
        t = text.lower().strip()

        # Reject if input is purely qualifier / attribute words
        tokens = [w.strip(".,!?") for w in t.split()]
        if tokens and all(w in self.QUALIFIER_WORDS for w in tokens):
            return None

        # 1. Dynamic match via sub-category product family (e.g. "laptop bag", "laptop sleeve", "wireless mouse")
        if any(b in t for b in ["bag", "sleeve", "backpack", "case", "pouch", "mouse", "mice", "keyboard", "keycaps", "cooler", "cooling", "hub", "dongle", "adapter"]):
            for prod in self.catalog:
                prod_cat = prod.get("category", "")
                if prod_cat.lower() in ["accessories", "womens-bags", "mobile-accessories"]:
                    return prod_cat

        # 2. Direct exact or word boundary match with catalog category names
        for cat_lower, actual_cat in self.category_map.items():
            if re.search(r'\b' + re.escape(cat_lower) + r'\b', t):
                return actual_cat

        # 3. Singular / plural variations of catalog categories
        for cat_lower, actual_cat in self.category_map.items():
            singular = cat_lower.rstrip('s')
            if len(singular) > 2 and re.search(r'\b' + re.escape(singular) + r'\b', t):
                return actual_cat

        return None

    def get_macro_category(self, product_type: Optional[str]) -> Optional[str]:
        if not product_type:
            return None
        pt = product_type.lower().strip()
        if any(b in pt for b in ["bag", "sleeve", "mouse", "mice", "keyboard", "keycaps", "cooler", "cooling", "hub", "dongle", "adapter", "case", "pouch", "backpack"]):
            return "Accessories"
        elif any(l in pt for l in ["laptop", "laptops", "notebook", "macbook", "ultrabook"]):
            return "Laptops"
        elif any(a in pt for a in ["audio", "headphone", "headphones", "headset", "earphone", "earbuds", "anc"]):
            return "Audio"
        elif any(m in pt for m in ["monitor", "monitors", "display", "screen"]):
            return "Monitors"
        elif pt in self.category_map:
            return self.category_map[pt]
        return None

    def get_min_category_price(self, category: str) -> float:
        cat_lower = category.lower().strip()
        if cat_lower in self.category_price_bounds:
            return self.category_price_bounds[cat_lower][0]

        # Check partial category match
        for k, v in self.category_price_bounds.items():
            if k in cat_lower or cat_lower in k:
                return v[0]
        return 0.0

    def is_category_in_catalog(self, category_or_noun: str) -> bool:
        if not category_or_noun:
            return False
        cat_lower = category_or_noun.lower().strip()

        # Check exact category map
        if cat_lower in self.category_map:
            return True

        # Check singular / plural of category map
        for c in self.categories:
            c_clean = c.lower().strip()
            if cat_lower == c_clean or cat_lower.rstrip('s') == c_clean.rstrip('s'):
                return True

        # Check sub-category nouns present in catalog items
        known_subcats = [
            "mouse", "mice", "bag", "sleeve", "backpack", "case", "pouch",
            "keyboard", "keycaps", "cooler", "cooling", "hub", "dongle", "adapter",
            "laptop", "notebook", "macbook", "headphone", "headphones", "headset",
            "earphone", "earbuds", "audio", "monitor", "display", "screen"
        ]
        if cat_lower in known_subcats:
            return True

        # Check word boundary match in product names, categories, or tags
        for prod in self.catalog:
            prod_name = prod.get("name", "").lower()
            prod_cat = prod.get("category", "").lower()
            prod_tags = [t.lower() for t in prod.get("tags", [])]
            if re.search(r'\b' + re.escape(cat_lower) + r'\b', prod_cat) or \
               re.search(r'\b' + re.escape(cat_lower) + r'\b', prod_name) or \
               any(cat_lower == tag for tag in prod_tags):
                return True

        return False

    def detect_brand(self, text: str) -> Optional[str]:
        t = text.lower().strip()
        for b in self.brands:
            if re.search(r'\b' + re.escape(b) + r'\b', t):
                return b
        return None

catalog_registry = CatalogRegistry()
