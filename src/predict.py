"""
ThreatText AI - Unified Prediction & Batch Inference Engine
Supports multi-model inference across Logistic Regression, Linear SVM, and Multinomial Naive Bayes.
Handles single email analysis and bulk CSV processing with probability calibration.
"""

import os
import io
import sys
import joblib
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Tuple

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.preprocessing import clean_email_text, parse_raw_email, parse_email_file

MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

class ThreatPredictor:
    def __init__(self):
        self.models = {}
        self.vectorizer = None
        self._load_artifacts()

    def _load_artifacts(self):
        vec_path = os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib")
        if os.path.exists(vec_path):
            self.vectorizer = joblib.load(vec_path)

        # Primary Logistic Regression
        lr_path = os.path.join(MODELS_DIR, "phishing_model.joblib")
        if os.path.exists(lr_path):
            self.models["logistic_regression"] = joblib.load(lr_path)

        # Naive Bayes
        nb_path = os.path.join(MODELS_DIR, "naive_bayes_model.joblib")
        if os.path.exists(nb_path):
            self.models["naive_bayes"] = joblib.load(nb_path)

        # Linear SVM
        svm_path = os.path.join(MODELS_DIR, "linear_svm_model.joblib")
        if os.path.exists(svm_path):
            self.models["linear_svm"] = joblib.load(svm_path)

    def is_ready(self) -> bool:
        return self.vectorizer is not None and len(self.models) > 0

    def get_available_models(self) -> List[Dict[str, str]]:
        descriptions = {
            "logistic_regression": "Logistic Regression (Primary XAI - Direct Signed Weights)",
            "linear_svm": "Linear Support Vector Machine (Calibrated Max-Margin)",
            "naive_bayes": "Multinomial Naive Bayes (Log-Odds Probabilistic)"
        }
        return [
            {"id": key, "name": descriptions.get(key, key), "is_primary": (key == "logistic_regression")}
            for key in self.models.keys()
        ]

    def predict_single(
        self,
        raw_text: str,
        subject: str = "",
        model_name: str = "logistic_regression"
    ) -> Dict[str, Any]:
        """
        Runs single-email inference using the selected model.
        """
        if not self.is_ready():
            return {
                "error": "Models are not loaded. Run train.py or train.bat first.",
                "prediction": "Unknown",
                "risk_score_pct": 0.0,
                "threat_level": "Unknown"
            }

        # Choose model
        model = self.models.get(model_name)
        if model is None:
            # Fallback to primary
            model = self.models.get("logistic_regression") or next(iter(self.models.values()))
            model_name = "logistic_regression"

        # Combine subject and body if provided
        combined_text = f"Subject: {subject}\n\n{raw_text}" if subject.strip() else raw_text
        cleaned = clean_email_text(combined_text)

        if not cleaned or len(cleaned.strip()) < 5:
            return {
                "error": "Email text contains insufficient readable content for NLP analysis.",
                "prediction": "Legitimate",
                "risk_score_pct": 0.0,
                "threat_level": "Safe / Likely Legitimate",
                "threat_badge_color": "#10b981",
                "threat_bg": "#f0fdf4"
            }

        vec = self.vectorizer.transform([cleaned])

        # Compute probability
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(vec)[0]
            phish_prob = float(probs[1])
            legit_prob = float(probs[0])
        else:
            decision = model.decision_function(vec)[0]
            phish_prob = float(1.0 / (1.0 + np.exp(-decision)))
            legit_prob = 1.0 - phish_prob

        prediction_label = "Phishing" if phish_prob >= 0.50 else "Legitimate"
        risk_score_pct = round(phish_prob * 100, 2)

        # Categorize Threat Level
        if risk_score_pct >= 75:
            threat_level = "Critical Threat"
            threat_badge_color = "#ef4444"
            threat_bg = "#fef2f2"
        elif risk_score_pct >= 50:
            threat_level = "Suspicious Risk"
            threat_badge_color = "#f97316"
            threat_bg = "#fff7ed"
        elif risk_score_pct >= 25:
            threat_level = "Low/Guarded Risk"
            threat_badge_color = "#eab308"
            threat_bg = "#fefce8"
        else:
            threat_level = "Safe / Likely Legitimate"
            threat_badge_color = "#10b981"
            threat_bg = "#f0fdf4"

        return {
            "prediction": prediction_label,
            "model_used": model_name,
            "phishing_probability": round(phish_prob, 4),
            "legitimate_probability": round(legit_prob, 4),
            "risk_score_pct": risk_score_pct,
            "threat_level": threat_level,
            "threat_badge_color": threat_badge_color,
            "threat_bg": threat_bg,
            "cleaned_char_count": len(cleaned),
            "original_char_count": len(combined_text)
        }

    def predict_batch_csv(
        self,
        csv_file_content: str,
        model_name: str = "logistic_regression",
        max_rows: int = 500
    ) -> Dict[str, Any]:
        """
        Parses CSV data, identifies text column, runs batch inference,
        and returns both summary statistics and row-level enriched data.
        """
        if not self.is_ready():
            raise RuntimeError("Models not loaded.")

        # Read CSV with robust fallback for stray commas
        try:
            df = pd.read_csv(io.StringIO(csv_file_content), on_bad_lines="skip")
        except Exception as e:
            raise ValueError(f"Failed to parse CSV file: {str(e)}")

        if len(df) == 0:
            raise ValueError("Uploaded CSV is empty.")

        # Limit to max_rows for browser responsiveness
        if len(df) > max_rows:
            df = df.iloc[:max_rows].copy()

        # Identify email text column
        text_col = None
        for col in df.columns:
            c_low = str(col).strip().lower()
            if any(term in c_low for term in ["text", "body", "email", "message", "content"]):
                text_col = col
                break

        # Fallback: choose object column with highest average string length
        if text_col is None:
            obj_cols = df.select_dtypes(include=["object"]).columns
            if len(obj_cols) > 0:
                lens = {c: df[c].astype(str).str.len().mean() for c in obj_cols}
                text_col = max(lens, key=lens.get)
            else:
                raise ValueError("Could not find a text column for email content in the CSV.")

        # Preprocess column
        cleaned_series = df[text_col].astype(str).apply(clean_email_text)
        vecs = self.vectorizer.transform(cleaned_series)

        model = self.models.get(model_name) or self.models.get("logistic_regression") or next(iter(self.models.values()))

        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(vecs)[:, 1]
        else:
            decision = model.decision_function(vecs)
            probs = 1.0 / (1.0 + np.exp(-decision))

        preds = (probs >= 0.50).astype(int)
        labels = np.where(preds == 1, "Phishing", "Legitimate")
        risk_pcts = np.round(probs * 100, 2)

        def get_threat_level(pct):
            if pct >= 75:
                return "Critical Threat"
            if pct >= 50:
                return "Suspicious Risk"
            if pct >= 25:
                return "Low/Guarded Risk"
            return "Safe / Likely Legitimate"

        threat_levels = [get_threat_level(p) for p in risk_pcts]

        # Enriched DataFrame
        df["ThreatText_Prediction"] = labels
        df["ThreatText_RiskScore_Pct"] = risk_pcts
        df["ThreatText_ThreatLevel"] = threat_levels

        # Summary
        total_rows = len(df)
        phish_count = int(np.sum(preds == 1))
        legit_count = total_rows - phish_count

        # Rows list
        rows_output = []
        for i in range(len(df)):
            snippet = str(df[text_col].iloc[i])[:150]
            if len(str(df[text_col].iloc[i])) > 150:
                snippet += "..."
            rows_output.append({
                "row_id": i + 1,
                "snippet": snippet,
                "prediction": labels[i],
                "risk_score_pct": float(risk_pcts[i]),
                "threat_level": threat_levels[i]
            })

        # Generate enriched CSV string
        csv_out = df.to_csv(index=False)

        return {
            "total_analyzed": total_rows,
            "phishing_detected": phish_count,
            "legitimate_detected": legit_count,
            "phishing_percentage": round((phish_count / total_rows) * 100, 2) if total_rows > 0 else 0,
            "text_column_detected": text_col,
            "model_used": model_name,
            "rows": rows_output,
            "enriched_csv": csv_out
        }

if __name__ == "__main__":
    predictor = ThreatPredictor()
    print("Available models:", predictor.get_available_models())
    test_result = predictor.predict_single(
        "Urgent: Security alert on your PayPal account. Please click here to verify immediately."
    )
    print("Test inference:", test_result)
