from typing import List, Dict, Any, Optional
from app.agent.ranking_engine import ranking_engine
from app.agent.tools import load_catalog

class GoalBasedBundleEngine:
    """
    Goal-Based Shopping Bundle Engine.
    Constructs multi-product bundles tailored to customer goals (e.g., complete programming setup)
    while adhering strictly to total budget constraints.
    """

    @classmethod
    def create_goal_bundle(cls, goal_query: str, total_budget: float = 70000.0) -> Dict[str, Any]:
        catalog = load_catalog()

        # Reserve at least 3,500 INR for accessories (mouse + sleeve/bag)
        laptop_max = max(10000.0, total_budget - 3500.0)
        laptops = [p for p in catalog if p.get("category") == "Laptops" and p.get("price", 0) <= laptop_max]
        ranked_laptops = ranking_engine.rank_catalog(laptops, query="laptop for programming", max_price=laptop_max)
        
        selected_laptop = ranked_laptops[0]["product"] if ranked_laptops else catalog[0]
        remaining_budget = total_budget - float(selected_laptop["price"])

        # Select Mouse
        mice = [p for p in catalog if "mouse" in p.get("tags", []) and p.get("price", 0) <= remaining_budget]
        ranked_mice = ranking_engine.rank_catalog(mice, query="ergonomic mouse", max_price=remaining_budget)
        selected_mouse = ranked_mice[0]["product"] if ranked_mice else None
        
        if selected_mouse:
            remaining_budget -= float(selected_mouse["price"])

        # Select Sleeve or Bag
        sleeves = [p for p in catalog if ("sleeve" in p.get("tags", []) or "bag" in p.get("tags", [])) and p.get("price", 0) <= remaining_budget]
        ranked_sleeves = ranking_engine.rank_catalog(sleeves, query="laptop sleeve", max_price=remaining_budget)
        selected_sleeve = ranked_sleeves[0]["product"] if ranked_sleeves else None

        if selected_sleeve:
            remaining_budget -= float(selected_sleeve["price"])

        # Optional Keyboard or Hub if budget permits
        selected_extra = None
        if remaining_budget >= 1500:
            extras = [p for p in catalog if ("hub" in p.get("tags", []) or "keyboard" in p.get("tags", [])) and p.get("price", 0) <= remaining_budget]
            ranked_extras = ranking_engine.rank_catalog(extras, query="developer accessory", max_price=remaining_budget)
            if ranked_extras:
                selected_extra = ranked_extras[0]["product"]
                remaining_budget -= float(selected_extra["price"])

        bundle_items = [selected_laptop]
        if selected_mouse:
            bundle_items.append(selected_mouse)
        if selected_sleeve:
            bundle_items.append(selected_sleeve)
        if selected_extra:
            bundle_items.append(selected_extra)

        total_cost = sum(float(p["price"]) for p in bundle_items)
        rem_budget = total_budget - total_cost

        item_summary = "\n".join([f"• **{p['name']}** — ₹{p['price']:,}" for p in bundle_items])
        explanation = (
            f"🎯 **Complete Goal Setup Bundle Recommendation:**\n\n"
            f"{item_summary}\n\n"
            f"💰 **Total Bundle Cost:** **₹{total_cost:,.0f}**\n"
            f"💵 **Remaining Budget:** **₹{rem_budget:,.0f}** (Out of ₹{total_budget:,.0f})\n\n"
            f"Why this bundle matches your goal:\n"
            f"• Sourced high-performance developer laptop ({selected_laptop['name']})\n"
            f"• Paired with ergonomic peripherals & protective sleeve for a complete workstation\n"
            f"• Fully stays within your ₹{total_budget:,.0f} budget constraint."
        )

        return {
            "bundle_title": "Complete Developer Setup Bundle",
            "items": bundle_items,
            "total_cost": total_cost,
            "remaining_budget": rem_budget,
            "total_budget": total_budget,
            "explanation": explanation
        }

bundle_engine = GoalBasedBundleEngine()
