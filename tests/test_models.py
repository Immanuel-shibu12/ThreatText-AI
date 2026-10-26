"""
ThreatText AI - Unit Tests for Multi-Model Inference & Performance
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.predict import ThreatPredictor

class TestModels(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.predictor = ThreatPredictor()

    def test_models_loaded(self):
        self.assertTrue(self.predictor.is_ready(), "Predictor should be ready with loaded models.")
        models = self.predictor.get_available_models()
        model_ids = [m["id"] for m in models]
        self.assertIn("logistic_regression", model_ids)
        self.assertIn("linear_svm", model_ids)
        self.assertIn("naive_bayes", model_ids)

    def test_phishing_detection_logistic_regression(self):
        phish_text = (
            "URGENT: Your bank account access has been temporarily restricted due to unauthorized login attempts. "
            "Please verify your credentials and password immediately at http://192.168.1.1/verify to prevent permanent closure."
        )
        res = self.predictor.predict_single(phish_text, model_name="logistic_regression")
        self.assertEqual(res["prediction"], "Phishing")
        self.assertGreaterEqual(res["risk_score_pct"], 75.0)
        self.assertIn(res["threat_level"], ["Critical Threat", "Suspicious Risk"])

    def test_legitimate_detection_logistic_regression(self):
        legit_text = (
            "Hi team, please find attached the slide deck and notes from yesterday's engineering meeting. "
            "Let's reconvene on Friday at 2:00 PM for the sprint planning session. Thank you."
        )
        res = self.predictor.predict_single(legit_text, model_name="logistic_regression")
        self.assertEqual(res["prediction"], "Legitimate")
        self.assertLess(res["risk_score_pct"], 50.0)

    def test_linear_svm_inference(self):
        phish_text = "Urgent: Click here to claim your $1,000 refund and update your banking password now."
        res = self.predictor.predict_single(phish_text, model_name="linear_svm")
        self.assertIn(res["prediction"], ["Phishing", "Legitimate"])
        self.assertGreaterEqual(res["risk_score_pct"], 0.0)
        self.assertLessEqual(res["risk_score_pct"], 100.0)

    def test_naive_bayes_inference(self):
        phish_text = "Security alert: unauthorized access to your account. Verify identity immediately."
        res = self.predictor.predict_single(phish_text, model_name="naive_bayes")
        self.assertIn(res["prediction"], ["Phishing", "Legitimate"])
        self.assertGreaterEqual(res["risk_score_pct"], 0.0)
        self.assertLessEqual(res["risk_score_pct"], 100.0)

    def test_batch_csv_prediction(self):
        sample_csv = """id,email_text
1,Urgent: Your account is suspended. Verify password at http://fake.com
2,Please join us for lunch tomorrow to celebrate the team milestone.
3,Security warning: confirm banking identity or face 50 dollar penalty.
"""
        batch_res = self.predictor.predict_batch_csv(sample_csv)
        self.assertEqual(batch_res["total_analyzed"], 3)
        self.assertGreaterEqual(batch_res["phishing_detected"], 1)
        self.assertEqual(len(batch_res["rows"]), 3)
        self.assertIn("ThreatText_Prediction", batch_res["enriched_csv"])

if __name__ == "__main__":
    unittest.main()
