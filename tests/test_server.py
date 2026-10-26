"""
ThreatText AI - Integration Tests for Localhost Web Server & REST APIs
Tests HTTP endpoints on http.server without requiring external frameworks.
"""

import os
import sys
import json
import time
import threading
import unittest
import urllib.request
import urllib.parse
from http.server import ThreadingHTTPServer

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from app import ThreatTextHTTPHandler

TEST_PORT = 8011
BASE_URL = f"http://127.0.0.1:{TEST_PORT}"

class TestServerAPIs(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", TEST_PORT), ThreatTextHTTPHandler)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.server_thread.start()
        time.sleep(0.5)  # Allow server to bind

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_get_root_serves_html(self):
        req = urllib.request.Request(f"{BASE_URL}/")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            self.assertIn("text/html", resp.headers.get("Content-Type", ""))
            content = resp.read().decode("utf-8")
            self.assertIn("ThreatText AI", content)

    def test_api_status(self):
        req = urllib.request.Request(f"{BASE_URL}/api/status")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data["status"], "online")
            self.assertEqual(data["total_samples"], 17512)

    def test_api_dataset_stats(self):
        req = urllib.request.Request(f"{BASE_URL}/api/dataset-stats")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(data["status"], "success")
            self.assertEqual(data["total_records"], 17512)
            self.assertEqual(data["missing_text_count"], 0)
            self.assertEqual(data["duplicate_records_found"], 0)

    def test_api_samples(self):
        req = urllib.request.Request(f"{BASE_URL}/api/samples")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            samples = json.loads(resp.read().decode("utf-8"))
            self.assertGreaterEqual(len(samples), 3)

    def test_api_analyze_phishing(self):
        payload = json.dumps({
            "subject": "URGENT: Bank Account Security Verification",
            "body": "Dear customer, your bank account access has been restricted. Please click here to verify your password immediately.",
            "model": "logistic_regression"
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{BASE_URL}/api/analyze",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(res["prediction"], "Phishing")
            self.assertGreaterEqual(res["risk_score_percent"], 50.0)
            self.assertIn("disclaimer", res)

    def test_api_analyze_legitimate(self):
        payload = json.dumps({
            "subject": "Weekly Department Lecture Timetable",
            "body": "Dear students, please find attached the revised lecture timetable and classroom assignments for next semester.",
            "model": "logistic_regression"
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{BASE_URL}/api/analyze",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(res["prediction"], "Legitimate")
            self.assertLess(res["risk_score_percent"], 50.0)

    def test_api_benchmarks(self):
        req = urllib.request.Request(f"{BASE_URL}/api/benchmarks")
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(res["test_set_size"], 3503)
            self.assertGreaterEqual(len(res["models"]), 3)

    def test_api_batch(self):
        csv_data = """id,email_text
1,"Urgent alert: verify password immediately at http://192.168.1.1/login"
2,"Team, attached is the revised meeting agenda for our design review."
"""
        payload = json.dumps({
            "csv_data": csv_data,
            "model": "logistic_regression"
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{BASE_URL}/api/batch",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            res = json.loads(resp.read().decode("utf-8"))
            self.assertEqual(res["total_analyzed"], 2)
            self.assertEqual(len(res["rows"]), 2)
            self.assertIn("ThreatText_Prediction", res["enriched_csv"])

if __name__ == "__main__":
    unittest.main()
