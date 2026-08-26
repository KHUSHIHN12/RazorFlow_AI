import os
import sys
import unittest

# Ensure backend app is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.agent.graph import agent_engine
from app.agent.ranking_engine import ranking_engine

class TestCommercePilotAgentScenarios(unittest.TestCase):

    def test_scenario_1_programming_laptop_under_60k(self):
        res = agent_engine.process_message("I need a laptop for programming under ₹60,000.", current_cart=[])
        self.assertTrue("ZenBook Pro 14" in res["response"] or "ThinkPad E14" in res["response"])
        self.assertTrue(len(res["products"]) > 0)
        self.assertLessEqual(res["products"][0]["price"], 60000)
        self.assertIn("Why I recommend it", res["response"])
        self.assertTrue(len(res["audit_logs"]) > 0)

    def test_scenario_2_best_value_laptop(self):
        res = agent_engine.process_message("I want the best value laptop under ₹60,000.", current_cart=[])
        self.assertTrue(len(res["products"]) > 0)
        self.assertLessEqual(res["products"][0]["price"], 60000)

    def test_scenario_3_battery_focus(self):
        res = agent_engine.process_message("I care mostly about battery life.", current_cart=[])
        self.assertTrue("MacBook Air M2" in res["response"] or "ZenBook Pro 14" in res["response"])
        self.assertTrue(len(res["products"]) > 0)

    def test_scenario_4_compare_top_laptops(self):
        res = agent_engine.process_message("Compare the top two laptops.", current_cart=[])
        self.assertIn("Side-by-Side Product Comparison", res["response"])
        self.assertGreaterEqual(len(res["products"]), 2)

    def test_scenario_5_add_to_cart(self):
        res = agent_engine.process_message("Add the recommended laptop to my cart.", current_cart=[])
        self.assertEqual(len(res["cart"]), 1)
        self.assertIn("Added", res["response"])

    def test_scenario_6_contextual_cross_sell(self):
        cart_item = [{"product_id": "prod_lap_01", "name": "ZenBook Pro 14", "price": 58999, "price_paise": 5899900, "quantity": 1}]
        res = agent_engine.process_message("What else should I buy with this laptop?", current_cart=cart_item)
        self.assertTrue("Cross-Sell" in res["response"] or "recommend" in res["response"])
        self.assertTrue(len(res["products"]) > 0)

    def test_scenario_7_complete_setup_bundle_under_70k(self):
        res = agent_engine.process_message("I need a complete programming setup under ₹70,000.", current_cart=[])
        self.assertIn("Complete Goal Setup Bundle", res["response"])
        self.assertIsNotNone(res["bundle_data"])
        self.assertLessEqual(res["bundle_data"]["total_cost"], 70000)
        self.assertGreaterEqual(len(res["products"]), 2)

    def test_scenario_8_buy_laptop_guardrail(self):
        cart_item = [{"product_id": "prod_lap_01", "name": "ZenBook Pro 14", "price": 58999, "price_paise": 5899900, "quantity": 1, "selected": True}]
        res = agent_engine.process_message("Buy this laptop.", current_cart=cart_item)
        self.assertTrue(res["confirmation_required"])
        self.assertIn("Payment Confirmation Required", res["response"])
        self.assertIsNone(res["active_order"])

        # Test explicit confirmation
        confirm_res = agent_engine.process_message("Yes, proceed to pay", current_cart=cart_item, confirmed_pay=True)
        self.assertIsNotNone(confirm_res["active_order"])
        self.assertFalse(confirm_res["confirmation_required"])
        self.assertIn("Razorpay Order Generated", confirm_res["response"])

    def test_scenario_9_voice_shopping_simulation(self):
        res = agent_engine.process_message("Find me a laptop under sixty thousand", current_cart=[])
        self.assertTrue(len(res["products"]) > 0)
        self.assertLessEqual(res["products"][0]["price"], 60000)

    def test_scenario_10_selective_checkout_unselected_remains(self):
        multi_cart = [
            {"product_id": "prod_lap_01", "name": "ZenBook Pro 14", "price": 58999, "price_paise": 5899900, "quantity": 1, "selected": True},
            {"product_id": "prod_acc_01", "name": "Precision Ergonomic Mouse", "price": 2499, "price_paise": 249900, "quantity": 1, "selected": False}
        ]
        res = agent_engine.process_message("Buy only the laptop.", current_cart=multi_cart)
        self.assertTrue(res["confirmation_required"])
        
        # Explicit confirmation
        confirm_res = agent_engine.process_message("Yes, proceed to pay", current_cart=multi_cart, confirmed_pay=True)
        self.assertIsNotNone(confirm_res["active_order"])
        self.assertEqual(confirm_res["active_order"]["amount_paise"], 5899900)
        self.assertEqual(len(confirm_res["active_order"]["items"]), 1)
        self.assertEqual(len(confirm_res["cart"]), 2)

    def test_scenario_11_watch_out_of_catalog(self):
        # Query for watch must NOT return laptops!
        res = agent_engine.process_message("I need a watch", current_cart=[])
        self.assertIn("Product Category Not Found in Catalog", res["response"])
        self.assertEqual(len(res["products"]), 0)
        # Ensure no laptop is returned in products array
        for prod in res["products"]:
            self.assertNotEqual(prod.get("category"), "Laptops")

    def test_scenario_12_laptop_carry_bag(self):
        # Query for laptop carry bag must return bag/sleeve, NOT laptop!
        res = agent_engine.process_message("I need a laptop carry bag", current_cart=[])
        self.assertTrue(len(res["products"]) > 0)
        best_prod = res["products"][0]
        self.assertEqual(best_prod.get("category"), "Accessories")
        self.assertTrue("sleeve" in best_prod.get("name", "").lower() or "bag" in best_prod.get("name", "").lower())

    def test_scenario_13_laptop_bag_under_2k(self):
        res = agent_engine.process_message("laptop bag under ₹2,000", current_cart=[])
        self.assertTrue(len(res["products"]) > 0)
        self.assertLessEqual(res["products"][0]["price"], 2000)
        self.assertEqual(res["products"][0]["category"], "Accessories")

    def test_scenario_14_wireless_mouse(self):
        res = agent_engine.process_message("wireless mouse", current_cart=[])
        self.assertTrue(len(res["products"]) > 0)
        self.assertEqual(res["products"][0]["category"], "Accessories")
        self.assertTrue("mouse" in res["products"][0]["name"].lower())

    def test_scenario_15_gaming_mouse_under_2k(self):
        res = agent_engine.process_message("gaming mouse under ₹2,000", current_cart=[])
        self.assertTrue(len(res["products"]) > 0)
        self.assertTrue("mouse" in res["products"][0]["name"].lower())

    def test_scenario_16_multi_turn_laptop_to_bag(self):
        # Turn 1: "I need a laptop"
        t1 = agent_engine.process_message("I need a laptop", current_cart=[])
        self.assertEqual(t1["products"][0]["category"], "Laptops")

        # Turn 2: "I also need a carry bag" -> Must return laptop bag, NOT laptop!
        t2 = agent_engine.process_message("I also need a carry bag", current_cart=[])
        self.assertEqual(t2["products"][0]["category"], "Accessories")
        self.assertTrue("sleeve" in t2["products"][0]["name"].lower() or "bag" in t2["products"][0]["name"].lower())

    def test_scenario_17_add_laptop_bag_to_cart(self):
        res = agent_engine.process_message("Add the laptop bag to my cart.", current_cart=[])
        self.assertTrue(len(res["cart"]) > 0)
        added_item = res["cart"][-1]
        self.assertTrue("sleeve" in added_item["name"].lower() or "bag" in added_item["name"].lower())

    def test_scenario_18_voice_and_text_parity(self):
        text_res = agent_engine.process_message("I need a laptop carry bag", current_cart=[])
        voice_stt_res = agent_engine.process_message("I need a laptop carry bag", current_cart=[])
        self.assertEqual(text_res["products"][0]["id"], voice_stt_res["products"][0]["id"])
        self.assertEqual(text_res["response"], voice_stt_res["response"])

    def test_buying_list_rule_1_cart_5_items_initially_empty(self):
        five_cart = [
            {"product_id": f"p{i}", "name": f"Item {i}", "price": 1000, "price_paise": 100000, "quantity": 1, "selected": False}
            for i in range(1, 6)
        ]
        res = agent_engine.process_message("What is in my cart?", current_cart=five_cart)
        selected_in_cart = [i for i in res["cart"] if i.get("selected") is True]
        self.assertEqual(len(selected_in_cart), 0)

    def test_buying_list_rule_2_select_1_item(self):
        cart = [
            {"product_id": "p1", "name": "Laptop", "price": 50000, "price_paise": 5000000, "quantity": 1, "selected": True},
            {"product_id": "p2", "name": "Mouse", "price": 1000, "price_paise": 100000, "quantity": 1, "selected": False},
            {"product_id": "p3", "name": "Keyboard", "price": 2000, "price_paise": 200000, "quantity": 1, "selected": False},
            {"product_id": "p4", "name": "Headphones", "price": 3000, "price_paise": 300000, "quantity": 1, "selected": False},
            {"product_id": "p5", "name": "Bag", "price": 1500, "price_paise": 150000, "quantity": 1, "selected": False}
        ]
        selected_items = [i for i in cart if i.get("selected") is True]
        self.assertEqual(len(selected_items), 1)
        self.assertEqual(selected_items[0]["name"], "Laptop")

    def test_buying_list_rule_3_select_2_items(self):
        cart = [
            {"product_id": "p1", "name": "Laptop", "price": 50000, "price_paise": 5000000, "quantity": 1, "selected": True},
            {"product_id": "p2", "name": "Mouse", "price": 1000, "price_paise": 100000, "quantity": 1, "selected": True},
            {"product_id": "p3", "name": "Keyboard", "price": 2000, "price_paise": 200000, "quantity": 1, "selected": False},
            {"product_id": "p4", "name": "Headphones", "price": 3000, "price_paise": 300000, "quantity": 1, "selected": False},
            {"product_id": "p5", "name": "Bag", "price": 1500, "price_paise": 150000, "quantity": 1, "selected": False}
        ]
        selected_items = [i for i in cart if i.get("selected") is True]
        self.assertEqual(len(selected_items), 2)
        self.assertEqual([i["name"] for i in selected_items], ["Laptop", "Mouse"])

    def test_buying_list_rule_4_select_all_5_items(self):
        cart = [
            {"product_id": f"p{i}", "name": f"Item {i}", "price": 1000, "price_paise": 100000, "quantity": 1, "selected": True}
            for i in range(1, 6)
        ]
        selected_items = [i for i in cart if i.get("selected") is True]
        self.assertEqual(len(selected_items), 5)

    def test_buying_list_rule_5_unselect_remains_in_cart(self):
        cart = [
            {"product_id": "p1", "name": "Laptop", "price": 50000, "price_paise": 5000000, "quantity": 1, "selected": False},
            {"product_id": "p2", "name": "Mouse", "price": 1000, "price_paise": 100000, "quantity": 1, "selected": True}
        ]
        # p1 was unselected (selected: False). It must remain in cart.
        self.assertEqual(len(cart), 2)
        selected_items = [i for i in cart if i.get("selected") is True]
        self.assertEqual(len(selected_items), 1)
        self.assertEqual(selected_items[0]["product_id"], "p2")

    def test_buying_list_rule_6_add_new_item_not_automatically_selected(self):
        res = agent_engine.process_message("Add the recommended laptop to my cart.", current_cart=[])
        self.assertEqual(len(res["cart"]), 1)
        added_item = res["cart"][0]
        self.assertFalse(added_item.get("selected", False))

    def test_buying_list_rule_7_checkout_only_buying_list_items(self):
        cart = [
            {"product_id": "p1", "name": "Laptop", "price": 50000, "price_paise": 5000000, "quantity": 1, "selected": True},
            {"product_id": "p2", "name": "Mouse", "price": 1000, "price_paise": 100000, "quantity": 1, "selected": True},
            {"product_id": "p3", "name": "Keyboard", "price": 2000, "price_paise": 200000, "quantity": 1, "selected": False}
        ]
        res = agent_engine.process_message("Yes, proceed to pay", current_cart=cart, confirmed_pay=True)
        self.assertIsNotNone(res["active_order"])
        # Total must match only 50000 + 1000 = 51000 (5100000 paise), excluding p3 Keyboard
        self.assertEqual(res["active_order"]["amount_paise"], 5100000)
        self.assertEqual(len(res["active_order"]["items"]), 2)

    def test_out_of_budget_alternative_suggestion(self):
        res = agent_engine.process_message("I need a laptop for coding under ₹30,000", current_cart=[])
        self.assertIn("No Suitable Products Found Within Your Budget", res["response"])
        self.assertTrue(len(res["products"]) > 0)
        closest_p = res["products"][0]
        self.assertGreater(closest_p["price"], 30000)
        self.assertEqual(closest_p["category"], "Laptops")
        self.assertIn("Closest Available Alternative", res["response"])

    def test_explicit_case_1_laptop_bag(self):
        res = agent_engine.process_message("laptop bag", current_cart=[])
        self.assertTrue(len(res["products"]) > 0)
        self.assertEqual(res["products"][0]["category"], "Accessories")
        self.assertTrue("bag" in res["products"][0]["name"].lower() or "sleeve" in res["products"][0]["name"].lower())

    def test_explicit_case_2_laptop_carry_bag_under_2000(self):
        res = agent_engine.process_message("laptop carry bag under ₹2000", current_cart=[])
        self.assertTrue(len(res["products"]) > 0)
        self.assertEqual(res["products"][0]["category"], "Accessories")
        self.assertLessEqual(res["products"][0]["price"], 2000)

    def test_explicit_case_3_wireless_mouse_under_1500(self):
        res = agent_engine.process_message("wireless mouse under ₹1500", current_cart=[])
        self.assertIn("No Suitable Products Found Within Your Budget", res["response"])
        self.assertTrue(len(res["products"]) > 0)
        self.assertTrue("mouse" in res["products"][0]["name"].lower())
        self.assertGreater(res["products"][0]["price"], 1500)

    def test_explicit_case_4_headphones_under_5000(self):
        res = agent_engine.process_message("headphones under ₹5000", current_cart=[])
        self.assertTrue(len(res["products"]) > 0)
        self.assertEqual(res["products"][0]["category"], "Audio")
        self.assertLessEqual(res["products"][0]["price"], 5000)

    def test_explicit_case_5_laptop_for_coding_under_60000(self):
        res = agent_engine.process_message("laptop for coding under ₹60000", current_cart=[])
        self.assertTrue(len(res["products"]) > 0)
        self.assertEqual(res["products"][0]["category"], "Laptops")
        self.assertLessEqual(res["products"][0]["price"], 60000)

    def test_generic_attribute_intent_parsing(self):
        intent = ranking_engine.parse_intent("I want a 14 inch silver macbook laptop under ₹70,000 for coding")
        self.assertEqual(intent["category"], "Laptops")
        self.assertEqual(intent["head_noun"], "laptop")
        self.assertEqual(intent["brand"], "macbook")
        self.assertEqual(intent["color"], "silver")
        self.assertEqual(intent["size"], "14")
        self.assertEqual(intent["max_price"], 70000.0)

    def test_attribute_mismatch_handling(self):
        res = agent_engine.process_message("red mouse under ₹3000", current_cart=[])
        self.assertIn("No Exact Match Found for Specified Attribute", res["response"])
        self.assertTrue(len(res["products"]) > 0)
        self.assertEqual(res["products"][0]["category"], "Accessories")
        self.assertTrue("mouse" in res["products"][0]["name"].lower())

    def test_fallback_level_1_exact_match(self):
        res = agent_engine.process_message("wireless mouse under ₹3000", current_cart=[])
        self.assertTrue(len(res["products"]) > 0)
        self.assertEqual(res["products"][0]["category"], "Accessories")
        self.assertLessEqual(res["products"][0]["price"], 3000)

    def test_fallback_level_2_relaxed_attributes(self):
        res = agent_engine.process_message("blue wireless mouse under ₹3000", current_cart=[])
        self.assertIn("No Exact Match Found for Specified Attribute", res["response"])
        self.assertTrue(len(res["products"]) > 0)
        self.assertEqual(res["products"][0]["category"], "Accessories")

    def test_fallback_level_3_relaxed_budget(self):
        res = agent_engine.process_message("wireless mouse under ₹1500", current_cart=[])
        self.assertIn("No Suitable Products Found Within Your Budget", res["response"])
        self.assertTrue(len(res["products"]) > 0)
        self.assertEqual(res["products"][0]["category"], "Accessories")

    def test_fallback_level_4_no_category(self):
        res = agent_engine.process_message("smartphone under ₹30000", current_cart=[])
        self.assertIn("Product Category Not Found in Catalog", res["response"])
        self.assertEqual(len(res["products"]), 0)

    def test_structured_intent_extraction_kurta_set(self):
        intent = ranking_engine.parse_intent("blue kurta set for womens")
        self.assertEqual(intent["category"], "kurta set")
        self.assertEqual(intent["color"], "blue")
        self.assertEqual(intent["gender"], "female")

    def test_structured_intent_extraction_blue_kurta_womens_process(self):
        res = agent_engine.process_message("blue kurta set for womens", current_cart=[])
        self.assertIn("Product Category Not Found in Catalog", res["response"])
        self.assertEqual(len(res["products"]), 0)

    def test_cart_action_view(self):
        cart_item = [{
            "product_id": "acc_001",
            "name": "RazorFlow Precision Ergonomic Wireless Mouse",
            "price": 2499.0,
            "price_paise": 249900,
            "quantity": 1,
            "selected": True
        }]
        res = agent_engine.process_message("show my cart", current_cart=cart_item)
        self.assertIn("Your Shopping Cart", res["response"])
        self.assertIn("RazorFlow Precision Ergonomic Wireless Mouse", res["response"])

    def test_cart_action_remove_success(self):
        cart_item = [{
            "product_id": "acc_001",
            "name": "RazorFlow Precision Ergonomic Wireless Mouse",
            "price": 2499.0,
            "price_paise": 249900,
            "quantity": 1,
            "selected": True
        }]
        res = agent_engine.process_message("take out the mouse", current_cart=cart_item)
        self.assertIn("Removed", res["response"])
        self.assertEqual(len(res["cart"]), 0)

    def test_cart_action_remove_not_in_cart(self):
        cart_item = [{
            "product_id": "acc_001",
            "name": "RazorFlow Precision Ergonomic Wireless Mouse",
            "price": 2499.0,
            "price_paise": 249900,
            "quantity": 1,
            "selected": True
        }]
        res = agent_engine.process_message("delete headphones from cart", current_cart=cart_item)
        self.assertIn("Could not find", res["response"])
        self.assertEqual(len(res["cart"]), 1)

    def test_cart_action_update(self):
        cart_item = [{
            "product_id": "acc_001",
            "name": "RazorFlow Precision Ergonomic Wireless Mouse",
            "price": 2499.0,
            "price_paise": 249900,
            "quantity": 1,
            "selected": True
        }]
        res = agent_engine.process_message("change quantity of mouse to 3", current_cart=cart_item)
        self.assertIn("Updated", res["response"])
        self.assertEqual(res["cart"][0]["quantity"], 3)

if __name__ == "__main__":
    unittest.main()
