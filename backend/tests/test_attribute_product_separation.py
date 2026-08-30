import unittest
from app.agent.graph import agent_engine

class TestAttributeProductSeparation(unittest.TestCase):

    def test_laptop_bag_with_attributes(self):
        res = agent_engine.process_message("blue laptop bag for women under ₹2,000", current_cart=[])
        self.assertIn("bag", res["context"].get("head_noun", "").lower())
        self.assertEqual(res["context"].get("color"), "blue")
        self.assertEqual(res["context"].get("gender"), "female")
        self.assertEqual(res["context"].get("max_price"), 2000.0)

    def test_out_of_catalog_helicopter_with_attributes(self):
        res = agent_engine.process_message("blue helicopter for womens", current_cart=[])
        self.assertEqual(len(res["products"]), 0)
        self.assertEqual(res["context"].get("head_noun"), "helicopter")
        self.assertEqual(res["context"].get("color"), "blue")
        self.assertEqual(res["context"].get("gender"), "female")
        self.assertIn("helicopter", res["response"].lower())
        self.assertNotIn("womens", res["response"].lower().split("requested:**")[1].split("\n")[0] if "requested:**" in res["response"].lower() else "")

    def test_out_of_catalog_shoes_with_attributes(self):
        res = agent_engine.process_message("mens leather running shoes", current_cart=[])
        self.assertEqual(len(res["products"]), 0)
        self.assertEqual(res["context"].get("head_noun"), "running shoes")
        self.assertEqual(res["context"].get("gender"), "male")
        self.assertEqual(res["context"].get("material"), "leather")

    def test_headphones_with_attributes(self):
        res = agent_engine.process_message("red gaming headphones for kids under 5000", current_cart=[])
        self.assertEqual(res["context"].get("color"), "red")
        self.assertEqual(res["context"].get("use_case"), "gaming")
        self.assertEqual(res["context"].get("gender"), "kids")

if __name__ == "__main__":
    unittest.main()
