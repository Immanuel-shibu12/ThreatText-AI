"""
ThreatText AI - Unit Tests for NLP Preprocessing & Email Parsing
"""

import os
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.preprocessing import (
    strip_html_tags,
    normalize_urls_and_emails,
    clean_email_text,
    parse_raw_email
)

class TestPreprocessing(unittest.TestCase):

    def test_strip_html_tags(self):
        html_input = "<html><body><h1>Security Alert</h1><p>Please click here to verify.</p></body></html>"
        clean = strip_html_tags(html_input)
        self.assertNotIn("<h1>", clean)
        self.assertNotIn("<p>", clean)
        self.assertIn("Security Alert", clean)
        self.assertIn("Please click here to verify.", clean)

    def test_html_entity_unescaping(self):
        raw = "Alert &amp; Warning &lt; urgent &gt;"
        clean = strip_html_tags(raw)
        self.assertIn("&", clean)
        self.assertIn("<", clean)
        self.assertIn(">", clean)

    def test_url_normalization(self):
        raw_ip = "Click here: http://192.168.1.100/login to access your account."
        normalized = normalize_urls_and_emails(raw_ip)
        self.assertIn("ip_url_link", normalized)
        self.assertNotIn("192.168.1.100", normalized)

        raw_https = "Visit https://secure-bank.com/portal today."
        norm_https = normalize_urls_and_emails(raw_https)
        self.assertIn("secure_url_token", norm_https)

    def test_email_address_normalization(self):
        raw_email = "Contact admin@security-department.org for assistance."
        norm = normalize_urls_and_emails(raw_email)
        self.assertIn("email_address_token", norm)
        self.assertNotIn("admin@security-department.org", norm)

    def test_clean_email_text_negation_retention(self):
        # Crucial: negations like "not" or "never" must not be stripped
        sample = "We did not authorize this login and will never ask for your pin."
        cleaned = clean_email_text(sample)
        self.assertIn("not", cleaned)
        self.assertIn("never", cleaned)

    def test_empty_or_none_handling(self):
        self.assertEqual(clean_email_text(""), "")
        self.assertEqual(clean_email_text(None), "")
        self.assertEqual(strip_html_tags(""), "")

    def test_parse_raw_email_headers(self):
        eml_text = """From: Security Team <security@bank-verify.com>
To: Victim <victim@example.com>
Subject: URGENT: Account Suspension Notice
Date: Mon, 26 Oct 2026 10:00:00 +0000

Dear Customer, your account has been locked. Verify immediately.
"""
        parsed = parse_raw_email(eml_text)
        self.assertEqual(parsed["subject"], "URGENT: Account Suspension Notice")
        self.assertIn("security@bank-verify.com", parsed["from"])
        self.assertIn("locked", parsed["body"])

if __name__ == "__main__":
    unittest.main()
