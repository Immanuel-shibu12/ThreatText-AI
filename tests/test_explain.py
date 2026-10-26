"""
ThreatText AI - Unit Tests for Explainable AI (XAI) Feature Attribution
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.explain import ThreatExplainer

class TestExplain(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.explainer = ThreatExplainer()

    def test_explainer_ready(self):
        self.assertTrue(self.explainer.is_ready())

    def test_phishing_feature_attribution(self):
        phish_text = "URGENT: Your bank account password must be verified immediately or account suspended."
        res = self.explainer.explain(phish_text, model_name="logistic_regression")
        
        self.assertEqual(res["prediction"], "Phishing")
        self.assertGreater(len(res["top_phishing_indicators"]), 0)
        
        # Check that top phishing indicators contain security triggers like 'account', 'bank', 'urgent', or 'password'
        phish_words = [item["phrase"] for item in res["top_phishing_indicators"]]
        found_trigger = any(w in phish_words for w in ["account", "bank", "urgent", "password", "suspended", "immediately"])
        self.assertTrue(found_trigger, f"Expected phishing triggers in: {phish_words}")

        # Check highlighted HTML
        self.assertIn("class=\"xai-phish\"", res["highlighted_html"])

        # Check disclaimer is present
        self.assertIn("disclaimer", res)
        self.assertIn("probabilistic", res["disclaimer"].lower())

    def test_legitimate_feature_attribution(self):
        legit_text = "Dear members, the conference agenda and timetable for the university symposium are attached."
        res = self.explainer.explain(legit_text, model_name="logistic_regression")
        
        self.assertEqual(res["prediction"], "Legitimate")
        self.assertGreater(len(res["top_legitimate_indicators"]), 0)

    def test_global_features(self):
        phish_top, legit_top = self.explainer.get_global_top_features(top_n=10)
        self.assertEqual(len(phish_top), 10)
        self.assertEqual(len(legit_top), 10)
        self.assertTrue(all(p["weight"] > 0 for p in phish_top))
        self.assertTrue(all(l["weight"] < 0 for l in legit_top))

if __name__ == "__main__":
    unittest.main()
