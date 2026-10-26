"""
ThreatText AI - Native HTTP Web Application & REST Server
Engineered with pure Python standard library (http.server.ThreadingHTTPServer).
Zero external web framework dependencies (No Streamlit, No Flask, No FastAPI, No Django).
Hosts the full explainable NLP phishing detection system locally at http://127.0.0.1:8000.
"""

import os
import sys
import json
import time
import urllib.parse
import mimetypes
import subprocess
from http import HTTPStatus
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, Optional

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Ensure UTF-8 output compatibility on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from src.preprocessing import clean_email_text, parse_raw_email
from src.dataset import validate_and_inspect_dataset
from src.predict import ThreatPredictor
from src.explain import ThreatExplainer
from src.db import db_logger

# Directory Paths
WEB_DIR = os.path.join(PROJECT_ROOT, "web")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
SAMPLE_EMAILS_DIR = os.path.join(PROJECT_ROOT, "sample_emails")

# Initialize NLP Engines
print("[ThreatText AI] Initializing Predictor and Explainer engines...")
predictor = ThreatPredictor()
explainer = ThreatExplainer()

# Benchmark Demonstration Presets
DEMO_SAMPLES = [
    {
        "id": "bank_verification",
        "title": "Bank Account Urgent Suspension",
        "type": "Phishing",
        "badge": "Phishing Threat",
        "subject": "URGENT: Temporary Suspension on Online Banking Access",
        "sender": "Chase Security Alerts <service-notice@chase-secure-verify.net>",
        "date": "Mon, 26 Oct 2026 09:14:22 -0500",
        "body": (
            "Dear Valued Customer,\n\n"
            "We have detected multiple unauthorized login attempts to your online banking portal "
            "from an unrecognized IP address (194.26.29.112).\n\n"
            "For your security, access to your funds and bill payment features has been temporarily suspended.\n\n"
            "To restore your access immediately and avoid permanent account lock within 24 hours, "
            "you must verify your identity and confirm your account password using our secure verification server:\n\n"
            "http://chase-identity-auth-portal.com/login?verify=true&session=89327498234\n\n"
            "Failure to verify within 24 hours will result in permanent suspension and a $50 administrative fee."
        )
    },
    {
        "id": "college_timetable",
        "title": "College Class Schedule & Timetable",
        "type": "Legitimate",
        "badge": "Legitimate (Safe)",
        "subject": "Updated Lecture Timetable for Fall Semester - CS Dept",
        "sender": "Dr. Sarah Jenkins <sjenkins@university.edu>",
        "date": "Mon, 26 Oct 2026 11:30:15 -0500",
        "body": (
            "Dear Computer Science Students,\n\n"
            "Please find attached the revised lecture timetable for the upcoming Fall semester. "
            "Due to classroom renovations in Hall B, Natural Language Processing (CS 460) will now be held in Room 304.\n\n"
            "Office hours schedule:\n"
            "- Tuesday: 2:00 PM - 4:00 PM\n"
            "- Thursday: 10:00 AM - 12:00 PM\n\n"
            "Please review the syllabus on the campus portal and let me know if you have timetable conflicts.\n\n"
            "Best regards,\n"
            "Dr. Sarah Jenkins\n"
            "Department of Computer Science & Engineering"
        )
    },
    {
        "id": "delivery_credentials",
        "title": "Delivery Notification & Parcel Update",
        "type": "Phishing",
        "badge": "Phishing Threat",
        "subject": "Notice: Incomplete Delivery Address for Parcel #DHL-984210",
        "sender": "DHL Express Notification <tracking-update@dhl-parcel-redelivery.org>",
        "date": "Mon, 26 Oct 2026 08:02:11 -0500",
        "body": (
            "Important Notice from DHL Courier Services:\n\n"
            "Your incoming international package (#DHL-984210-US) could not be delivered on scheduled date "
            "because the recipient address format is incomplete.\n\n"
            "A small customs processing charge of $2.99 is required to reschedule redelivery to your door.\n\n"
            "Click here to confirm your street address and pay fee securely:\n"
            "http://192.168.1.88/dhl-package-update/verify\n\n"
            "If unpaid within 48 hours, package will be returned to sender overseas."
        )
    },
    {
        "id": "hr_payroll_update",
        "title": "HR Payroll Direct Deposit Update",
        "type": "Phishing",
        "badge": "Phishing Threat",
        "subject": "Action Required: Update Your Direct Deposit Bank Account Details",
        "sender": "Corporate HR Portal <hr-support@internal-benefits-update.cc>",
        "date": "Mon, 26 Oct 2026 14:10:00 -0500",
        "body": (
            "Hello Employee,\n\n"
            "During routine quarterly auditing, we noticed your direct deposit bank routing number "
            "requires re-validation for the upcoming salary disbursement cycle.\n\n"
            "Please confirm your banking password and account details immediately on the employee portal:\n"
            "http://portal-login-benefits.com/auth\n\n"
            "Failure to update by 5:00 PM will cause your payroll disbursement to be deferred."
        )
    },
    {
        "id": "workplace_meeting",
        "title": "Workplace Project Review & Agenda",
        "type": "Legitimate",
        "badge": "Legitimate (Safe)",
        "subject": "Agenda: ThreatText AI Architecture Review - Tomorrow 10:00 AM",
        "sender": "Alex Rivera <alex.rivera@enterprise.com>",
        "date": "Mon, 26 Oct 2026 16:45:00 -0500",
        "body": (
            "Hi Team,\n\n"
            "Here is the finalized agenda for our architecture review tomorrow:\n\n"
            "1. Overview of 17,512 email benchmark dataset and sanitation metrics\n"
            "2. TF-IDF unigram and bigram feature representations\n"
            "3. Evaluation of Logistic Regression, Linear SVM, and Naive Bayes on held-out test split\n"
            "4. Review of XAI signed feature attribution engine\n"
            "5. Q&A and next sprint timeline\n\n"
            "The slide deck is uploaded to the internal drive. See you all tomorrow!\n\n"
            "Alex"
        )
    }
]

class ThreatTextHTTPHandler(BaseHTTPRequestHandler):
    """Custom HTTP Request Handler serving static web assets and REST APIs."""

    def log_message(self, format, *args):
        # Clean terminal logging format
        sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {args[0]} - {args[1]} {args[2]}\n")

    def _set_headers(self, status_code: int = 200, content_type: str = "application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(HTTPStatus.OK)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # -------------------------------------------------------------
        # 1. REST JSON APIs
        # -------------------------------------------------------------
        if path == "/api/status":
            self._handle_api_status()
            return
        elif path == "/api/dataset-stats":
            self._handle_api_dataset_stats()
            return
        elif path == "/api/samples":
            self._handle_api_samples()
            return
        elif path == "/api/benchmarks":
            self._handle_api_benchmarks()
            return
        elif path == "/api/global-features":
            self._handle_api_global_features()
            return
        elif path == "/api/report":
            self._handle_api_report()
            return

        # -------------------------------------------------------------
        # 2. Static File Serving
        # -------------------------------------------------------------
        if path == "/" or path == "/index.html":
            self._serve_file(os.path.join(WEB_DIR, "index.html"), "text/html; charset=utf-8")
            return
        elif path.startswith("/css/"):
            file_rel = path[5:]
            self._serve_file(os.path.join(WEB_DIR, "css", file_rel), "text/css")
            return
        elif path.startswith("/js/"):
            file_rel = path[4:]
            self._serve_file(os.path.join(WEB_DIR, "js", file_rel), "application/javascript")
            return
        elif path.startswith("/assets/"):
            file_rel = path[8:]
            target = os.path.join(WEB_DIR, "assets", file_rel)
            mime, _ = mimetypes.guess_type(target)
            self._serve_file(target, mime or "image/jpeg")
            return
        elif path.startswith("/results/"):
            file_rel = path[9:]
            target = os.path.join(RESULTS_DIR, file_rel)
            mime, _ = mimetypes.guess_type(target)
            self._serve_file(target, mime or "application/octet-stream")
            return
        elif path == "/data/sample_batch.csv":
            self._serve_file(os.path.join(DATA_DIR, "sample_batch.csv"), "text/csv; charset=utf-8")
            return

        # 404 Not Found
        self._set_headers(HTTPStatus.NOT_FOUND, "text/plain")
        self.wfile.write(b"404 Not Found - ThreatText AI Server")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/analyze":
            self._handle_api_analyze()
        elif path == "/api/upload":
            self._handle_api_upload()
        elif path == "/api/batch":
            self._handle_api_batch()
        elif path == "/api/retrain":
            self._handle_api_retrain()
        else:
            self._set_headers(HTTPStatus.NOT_FOUND, "application/json")
            self.wfile.write(json.dumps({"error": f"Unknown endpoint {path}"}).encode("utf-8"))

    # -----------------------------------------------------------------
    # API Implementation Methods
    # -----------------------------------------------------------------
    def _handle_api_status(self):
        self._set_headers(HTTPStatus.OK)
        payload = {
            "status": "online",
            "system_name": "ThreatText AI",
            "host": "127.0.0.1",
            "port": 8000,
            "total_samples": 17512,
            "models_available": predictor.get_available_models(),
            "selected_primary": "logistic_regression",
            "accuracy_held_out": 0.9817,
            "recall_held_out": 0.9763,
            "models_ready": predictor.is_ready(),
            "mongodb_connected": db_logger.is_connected
        }
        self.wfile.write(json.dumps(payload).encode("utf-8"))

    def _handle_api_dataset_stats(self):
        self._set_headers(HTTPStatus.OK)
        stats = validate_and_inspect_dataset()
        self.wfile.write(json.dumps(stats).encode("utf-8"))

    def _handle_api_samples(self):
        self._set_headers(HTTPStatus.OK)
        self.wfile.write(json.dumps(DEMO_SAMPLES).encode("utf-8"))

    def _handle_api_benchmarks(self):
        self._set_headers(HTTPStatus.OK)
        comp_csv = os.path.join(RESULTS_DIR, "model_comparison.csv")
        models_data = []

        if os.path.exists(comp_csv):
            import pandas as pd
            df = pd.read_csv(comp_csv)
            for _, r in df.iterrows():
                models_data.append({
                    "model": str(r.get("Model", "Unknown")),
                    "accuracy": float(r.get("Accuracy", 0.0)),
                    "precision": float(r.get("Precision", 0.0)),
                    "recall": float(r.get("Recall", 0.0)),
                    "f1_score": float(r.get("F1-Score", 0.0)),
                    "roc_auc": float(r.get("ROC-AUC", 0.0)),
                    "train_time_sec": float(r.get("Train Time (s)", 0.0))
                })

        self.wfile.write(json.dumps({
            "test_set_size": 3503,
            "models": models_data
        }).encode("utf-8"))

    def _handle_api_global_features(self):
        self._set_headers(HTTPStatus.OK)
        phish, legit = explainer.get_global_top_features(top_n=20)
        self.wfile.write(json.dumps({
            "phishing_triggers": phish,
            "legitimate_anchors": legit
        }).encode("utf-8"))

    def _handle_api_report(self):
        report_path = os.path.join(RESULTS_DIR, "PROJECT_REPORT.md")
        if not os.path.exists(report_path):
            report_path = os.path.join(PROJECT_ROOT, "report", "ThreatText_AI_Project_Report.md")

        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                content = f.read()
            self._set_headers(HTTPStatus.OK, "text/markdown; charset=utf-8")
            self.wfile.write(content.encode("utf-8"))
        else:
            self._set_headers(HTTPStatus.NOT_FOUND, "text/plain")
            self.wfile.write(b"Report markdown file not found.")

    def _handle_api_analyze(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            body_json = json.loads(post_data.decode("utf-8"))
        except Exception as e:
            self._set_headers(HTTPStatus.BAD_REQUEST)
            self.wfile.write(json.dumps({"error": f"Invalid JSON payload: {str(e)}"}).encode("utf-8"))
            return

        subject = body_json.get("subject", "")
        email_body = body_json.get("body", "")
        model_name = body_json.get("model", "logistic_regression")

        if not email_body.strip():
            self._set_headers(HTTPStatus.BAD_REQUEST)
            self.wfile.write(json.dumps({"error": "Email body content is required."}).encode("utf-8"))
            return

        # Explain prediction
        try:
            result = explainer.explain(email_body, subject=subject, model_name=model_name)
            
            # Log to MongoDB if connected
            db_logger.log_scan(
                subject=subject,
                body_snippet=email_body,
                prediction=result.get("prediction", "Unknown"),
                risk_score_pct=result.get("risk_score_percent", 0.0),
                threat_level=result.get("threat_level", "Unknown"),
                model_used=model_name,
                top_phishing_triggers=result.get("top_phishing_indicators", [])
            )

            self._set_headers(HTTPStatus.OK)
            self.wfile.write(json.dumps(result).encode("utf-8"))
        except Exception as e:
            self._set_headers(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.wfile.write(json.dumps({"error": f"Inference error: {str(e)}"}).encode("utf-8"))

    def _handle_api_upload(self):
        """Handles .eml and .txt file upload."""
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)

        content_type = self.headers.get("Content-Type", "")

        # Handle multipart/form-data simple boundary extraction
        file_bytes = raw_body
        if "boundary=" in content_type:
            boundary = content_type.split("boundary=")[1].strip().encode()
            parts = raw_body.split(boundary)
            for part in parts:
                if b'filename="' in part:
                    # Strip headers of the part
                    header_end = part.find(b"\r\n\r\n")
                    if header_end != -1:
                        file_bytes = part[header_end + 4:].rstrip(b"\r\n--")
                        break

        # Decode content safely
        try:
            text_content = file_bytes.decode("utf-8", errors="replace")
        except Exception:
            text_content = file_bytes.decode("latin-1", errors="replace")

        # Parse RFC 822 email format
        parsed_email = parse_raw_email(text_content)
        subject = parsed_email.get("subject", "")
        body = parsed_email.get("body", "")

        # If body is empty, fallback to raw text
        if not body.strip():
            body = text_content

        # Run analysis
        try:
            analysis = explainer.explain(body, subject=subject)
            analysis["subject"] = subject
            analysis["body"] = body
            analysis["sender"] = parsed_email.get("from", "")
            analysis["date"] = parsed_email.get("date", "")

            self._set_headers(HTTPStatus.OK)
            self.wfile.write(json.dumps(analysis).encode("utf-8"))
        except Exception as e:
            self._set_headers(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.wfile.write(json.dumps({"error": f"Failed to analyze uploaded file: {str(e)}"}).encode("utf-8"))

    def _handle_api_batch(self):
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)

        try:
            body_json = json.loads(post_data.decode("utf-8"))
        except Exception as e:
            self._set_headers(HTTPStatus.BAD_REQUEST)
            self.wfile.write(json.dumps({"error": f"Invalid JSON payload: {str(e)}"}).encode("utf-8"))
            return

        csv_content = body_json.get("csv_data", "")
        model_name = body_json.get("model", "logistic_regression")

        if not csv_content.strip():
            self._set_headers(HTTPStatus.BAD_REQUEST)
            self.wfile.write(json.dumps({"error": "CSV data is empty."}).encode("utf-8"))
            return

        try:
            batch_result = predictor.predict_batch_csv(csv_content, model_name=model_name)
            self._set_headers(HTTPStatus.OK)
            self.wfile.write(json.dumps(batch_result).encode("utf-8"))
        except Exception as e:
            self._set_headers(HTTPStatus.BAD_REQUEST)
            self.wfile.write(json.dumps({"error": f"Batch processing failed: {str(e)}"}).encode("utf-8"))

    def _handle_api_retrain(self):
        """Triggers local training scripts and returns execution log."""
        t0 = time.time()
        try:
            train_script = os.path.join(PROJECT_ROOT, "src", "train.py")
            eval_script = os.path.join(PROJECT_ROOT, "src", "evaluate.py")

            cmd_train = [sys.executable, train_script]
            p_train = subprocess.run(cmd_train, capture_output=True, text=True, timeout=180)

            cmd_eval = [sys.executable, eval_script]
            p_eval = subprocess.run(cmd_eval, capture_output=True, text=True, timeout=120)

            duration = round(time.time() - t0, 2)
            combined_output = p_train.stdout + "\n" + p_eval.stdout
            if p_train.stderr:
                combined_output += "\n[Train Warnings/Errors]:\n" + p_train.stderr
            if p_eval.stderr:
                combined_output += "\n[Eval Warnings/Errors]:\n" + p_eval.stderr

            # Reload models
            predictor._load_artifacts()
            explainer._load_artifacts()

            self._set_headers(HTTPStatus.OK)
            self.wfile.write(json.dumps({
                "status": "success",
                "duration_sec": duration,
                "output": combined_output
            }).encode("utf-8"))

        except Exception as e:
            self._set_headers(HTTPStatus.INTERNAL_SERVER_ERROR)
            self.wfile.write(json.dumps({
                "status": "error",
                "error": f"Retraining execution failed: {str(e)}"
            }).encode("utf-8"))

    def _serve_file(self, full_path: str, content_type: str):
        if not os.path.exists(full_path):
            self._set_headers(HTTPStatus.NOT_FOUND, "text/plain")
            self.wfile.write(f"File not found: {os.path.basename(full_path)}".encode("utf-8"))
            return

        try:
            with open(full_path, "rb") as f:
                content = f.read()
            self._set_headers(HTTPStatus.OK, content_type)
            self.wfile.write(content)
        except Exception as e:
            self._set_headers(HTTPStatus.INTERNAL_SERVER_ERROR, "text/plain")
            self.wfile.write(f"Error reading file: {str(e)}".encode("utf-8"))

def run_server(host: str = "127.0.0.1", port: int = 8000):
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, ThreatTextHTTPHandler)

    print("=" * 68)
    print("      [+] ThreatText AI - Explainable NLP Phishing Detection System")
    print("=" * 68)
    print(f"  Server URL      : http://{host}:{port}")
    print(f"  Local Host      : http://127.0.0.1:{port}")
    print(f"  Dataset Records : 17,512 verified emails (Enron, Nazario, SpamAssassin)")
    print(f"  Supervised ML   : Logistic Regression, Linear SVM, Naive Bayes")
    print(f"  XAI Method      : Signed TF-IDF Feature Attribution (x_i * w_i)")
    print(f"  Architecture    : Pure Python http.server (No Flask / No Streamlit)")
    print("=" * 68)
    print("Press Ctrl+C in this terminal window to stop the server at any time.\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[ThreatText AI] Server shutting down cleanly...")
    finally:
        httpd.server_close()
        print("[ThreatText AI] Server stopped.")

if __name__ == "__main__":
    run_server()
