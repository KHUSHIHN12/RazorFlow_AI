import unittest
from app.agent.graph import agent_engine
from app.agent.context_manager import context_manager

class TestContextAndProductResolution(unittest.TestCase):

    def test_stale_context_isolation_and_out_of_catalog(self):
        # Turn 1: User asks for a programming laptop under 150k
        res1 = agent_engine.process_message("I need a laptop for programming under ₹150,000.", current_cart=[])
        self.assertTrue(len(res1["products"]) > 0)
        self.assertEqual(res1["context"]["category"], "Laptops")
        ctx1 = res1["context"]

        # Turn 2: User switches to monitors (new query, not a follow-up)
        res2 = agent_engine.process_message("show me monitors", current_cart=[], context=ctx1)
        self.assertTrue(len(res2["products"]) > 0)
        self.assertIn(res2["context"]["category"].lower(), ["monitors", "monitor"])
        self.assertIsNone(res2["context"].get("use_case"))  # Must NOT inherit 'programming'
        ctx2 = res2["context"]

        # Turn 3: User asks for an out-of-catalog item 'coffee maker'
        res3 = agent_engine.process_message("show me a coffee maker", current_cart=[], context=ctx2)
        self.assertEqual(len(res3["products"]), 0)  # Must be 0 product cards!
        self.assertIn("not featured in our store inventory", res3["response"].lower())
        self.assertNotIn("zenbook", res3["response"].lower())
        self.assertNotIn("huawei", res3["response"].lower())

    def test_followup_preservation(self):
        # Turn 1: Search laptops
        res1 = agent_engine.process_message("I need a laptop", current_cart=[])
        self.assertTrue(len(res1["products"]) > 0)
        self.assertEqual(res1["context"]["category"], "Laptops")
        ctx1 = res1["context"]

        # Turn 2: Follow-up query "show a cheaper one"
        res2 = agent_engine.process_message("show a cheaper one", current_cart=[], context=ctx1)
        self.assertTrue(len(res2["products"]) > 0)
        self.assertEqual(res2["context"]["category"], "Laptops")

    def test_ambiguous_query_prompt(self):
        res = agent_engine.process_message("show me something nice", current_cart=[])
        self.assertEqual(len(res["products"]), 0)
        self.assertIn("Clarification Required", res["response"])

if __name__ == "__main__":
    unittest.main()
