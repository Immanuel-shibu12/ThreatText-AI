"""
ThreatText AI - Unit Tests for Genuine Dataset Integrity & Validation
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.dataset import validate_and_inspect_dataset, DATA_CSV

class TestDataset(unittest.TestCase):

    def test_dataset_exists(self):
        self.assertTrue(os.path.exists(DATA_CSV), f"Dataset file missing at {DATA_CSV}")

    def test_dataset_integrity(self):
        stats = validate_and_inspect_dataset(DATA_CSV)
        self.assertEqual(stats["status"], "success")
        
        # Verify genuine records count matches canonical benchmark
        self.assertEqual(stats["total_records"], 17512)
        self.assertEqual(stats["legitimate_count"], 10976)
        self.assertEqual(stats["phishing_count"], 6536)

        # Check data sanitization: 0 nulls, 0 duplicate emails
        self.assertEqual(stats["missing_text_count"], 0)
        self.assertEqual(stats["missing_label_count"], 0)
        self.assertEqual(stats["duplicate_records_found"], 0)

        # Check documented sources and limitations are present
        self.assertGreater(len(stats["sources"]), 0)
        self.assertGreater(len(stats["limitations"]), 0)

if __name__ == "__main__":
    unittest.main()
