"""
ThreatText AI - Explainable AI (XAI) Module
Provides feature-level interpretability for email predictions using signed TF-IDF
contributions from trained supervised classifiers (Logistic Regression, Linear SVM, Naive Bayes).
Generates token-level attribution, highlighted HTML spans, and safety recommendations.
"""

import os
import sys
import re
import html
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List, Tuple, Optional

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")

class ThreatExplainer:
    def __init__(self):
        self.models = {}
        self.vectorizer = None
        self.feature_names = None
        self._load_artifacts()

    def _load_artifacts(self):
        vec_path = os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib")
        if os.path.exists(vec_path):
            self.vectorizer = joblib.load(vec_path)
            self.feature_names = np.array(self.vectorizer.get_feature_names_out())

        lr_path = os.path.join(MODELS_DIR, "phishing_model.joblib")
        if os.path.exists(lr_path):
            self.models["logistic_regression"] = joblib.load(lr_path)

        nb_path = os.path.join(MODELS_DIR, "naive_bayes_model.joblib")
        if os.path.exists(nb_path):
            self.models["naive_bayes"] = joblib.load(nb_path)

        svm_path = os.path.join(MODELS_DIR, "linear_svm_model.joblib")
        if os.path.exists(svm_path):
            self.models["linear_svm"] = joblib.load(svm_path)

    def is_ready(self) -> bool:
        return self.vectorizer is not None and len(self.models) > 0

    def get_feature_weights(self, model_name: str = "logistic_regression") -> Optional[np.ndarray]:
        """
        Extracts signed feature weights depending on the model architecture:
        - Logistic Regression: coef_[0]
        - Linear SVM: calibrated base estimator coef_
        - Naive Bayes: feature_log_prob_[1] - feature_log_prob_[0] (log-odds difference)
        """
        model = self.models.get(model_name) or self.models.get("logistic_regression")
        if model is None:
            return None

        # Logistic Regression
        if hasattr(model, "coef_"):
            return model.coef_[0]

        # Naive Bayes
        if hasattr(model, "feature_log_prob_"):
            # Difference in log probabilities between phishing (1) and legitimate (0)
            return model.feature_log_prob_[1] - model.feature_log_prob_[0]

        # CalibratedClassifierCV wrapping LinearSVC
        if hasattr(model, "calibrated_classifiers_"):
            try:
                base = model.calibrated_classifiers_[0].estimator
                if hasattr(base, "coef_"):
                    return base.coef_[0]
            except Exception:
                pass

        # Fallback to primary logistic regression weights
        lr = self.models.get("logistic_regression")
        if lr is not None and hasattr(lr, "coef_"):
            return lr.coef_[0]

        return None

    def explain(
        self,
        email_text: str,
        subject: str = "",
        top_k: int = 10,
        model_name: str = "logistic_regression"
    ) -> Dict[str, Any]:
        """
        Analyzes email text, computes prediction, class probabilities,
        and extracts signed linear feature contributions.
        """
        if not self.is_ready():
            raise RuntimeError("Model or vectorizer not loaded.")

        from src.preprocessing import clean_email_text
        combined = f"Subject: {subject}\n\n{email_text}" if subject.strip() else email_text
        cleaned = clean_email_text(combined)

        if not cleaned or len(cleaned.strip()) < 5:
            return {
                "error": "Email content is empty or contains no readable text.",
                "prediction": "Unknown",
                "risk_score_percent": 0.0,
                "threat_level": "None",
                "threat_badge_color": "#94a3b8",
                "threat_bg": "#f8fafc",
                "top_phishing_indicators": [],
                "top_legitimate_indicators": [],
                "total_active_features": 0,
                "recommendations": ["Please enter or upload valid email content for analysis."],
                "highlighted_html": html.escape(email_text),
                "disclaimer": "No email text provided for evaluation."
            }

        # Vectorize
        vec = self.vectorizer.transform([cleaned])

        # Pick model
        model = self.models.get(model_name) or self.models.get("logistic_regression") or next(iter(self.models.values()))
        
        # Probabilities
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

        # Threat Level Category
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

        # Local Feature Contribution Analysis
        # Contribution = x_i * w_i
        weights = self.get_feature_weights(model_name)
        
        phishing_features = []
        legitimate_features = []
        all_active_tokens = {}

        if weights is not None:
            non_zero_indices = vec.nonzero()[1]
            for idx in non_zero_indices:
                token = self.feature_names[idx]
                tf_idf_val = float(vec[0, idx])
                weight = float(weights[idx])
                contribution = tf_idf_val * weight

                all_active_tokens[token] = {
                    "token": token,
                    "tfidf": round(tf_idf_val, 4),
                    "coefficient": round(weight, 4),
                    "contribution": round(contribution, 4)
                }

                if contribution > 0:
                    phishing_features.append({
                        "phrase": token,
                        "influence": round(contribution, 4),
                        "direction": "Pushes towards Phishing",
                        "weight": round(weight, 3),
                        "tfidf": round(tf_idf_val, 3)
                    })
                elif contribution < 0:
                    legitimate_features.append({
                        "phrase": token,
                        "influence": round(abs(contribution), 4),
                        "direction": "Pushes towards Legitimate",
                        "weight": round(weight, 3),
                        "tfidf": round(tf_idf_val, 3)
                    })

            # Sort by absolute contribution strength
            phishing_features.sort(key=lambda x: x["influence"], reverse=True)
            legitimate_features.sort(key=lambda x: x["influence"], reverse=True)

        top_phishing = phishing_features[:top_k]
        top_legitimate = legitimate_features[:top_k]

        # Generate Actionable Security Recommendations
        recommendations = self._generate_recommendations(email_text, cleaned, top_phishing, phish_prob)

        # Generate Highlighted HTML Snippet
        highlighted_html = self._generate_highlighted_html(email_text, top_phishing, top_legitimate)

        disclaimer = (
            "Security Notice: ThreatText AI provides probabilistic NLP feature attribution "
            "for triage assistance. Predictions must not be treated as definitive cryptographic "
            "or security verdicts. Always inspect email sender origins and verification protocols."
        )

        return {
            "prediction": prediction_label,
            "model_used": model_name,
            "phishing_probability": round(phish_prob, 4),
            "legitimate_probability": round(legit_prob, 4),
            "risk_score_percent": risk_score_pct,
            "threat_level": threat_level,
            "threat_badge_color": threat_badge_color,
            "threat_bg": threat_bg,
            "top_phishing_indicators": top_phishing,
            "top_legitimate_indicators": top_legitimate,
            "total_active_features": len(all_active_tokens),
            "recommendations": recommendations,
            "highlighted_html": highlighted_html,
            "cleaned_text": cleaned,
            "disclaimer": disclaimer
        }

    def _generate_recommendations(self, raw_text: str, cleaned_text: str, phish_features: List[Dict], prob: float) -> List[str]:
        recs = []
        raw_lower = raw_text.lower()

        if prob >= 0.50:
            recs.append("⚠️ Do NOT click any links, open attachments, or reply to this message.")
            if any(w in raw_lower for w in ["password", "credential", "login", "verify your account", "account suspended"]):
                recs.append("🔒 Sensitive credential request: Legitimate institutions never ask for passwords or account verification via email links.")
            if any(w in raw_lower for w in ["urgent", "immediately", "within 24 hours", "suspended", "action required"]):
                recs.append("⏳ Artificial Urgency Detected: Attackers use panic triggers to rush you into acting without verification.")
            if "http_url_token" in cleaned_text or "ip_url_link" in cleaned_text or "http://" in raw_lower:
                recs.append("🌐 Insecure or direct-IP URLs detected: Inspect destination domains carefully for typosquatting (e.g., paypa1.com).")
            if any(w in raw_lower for w in ["bank", "wire transfer", "payment", "invoice", "gift card", "crypto"]):
                recs.append("💳 Financial fraud indicator: Contact the organization via official verified phone numbers before authorizing any transaction.")
            recs.append("🛡️ Action: Report this message to your organization's IT Security / Phishing response team.")
        else:
            recs.append("✅ Low Phishing Risk: The vocabulary and structural patterns align with normal legitimate correspondence.")
            recs.append("🔍 Standard Hygiene: Always check the sender's actual email domain (From header) matches the expected organization.")
            if "secure_url_token" in cleaned_text or "http" in raw_lower:
                recs.append("🔗 Links present: Even legitimate emails may contain links; hover over hyperlinks before clicking to confirm destination.")

        return recs

    def _generate_highlighted_html(self, raw_text: str, phish_feats: List[Dict], legit_feats: List[Dict]) -> str:
        """
        Creates clean, styled HTML markup with hover tags for influential words.
        """
        safe_text = html.escape(raw_text)
        
        # Phrases to highlight
        p_phrases = sorted([f["phrase"] for f in phish_feats if len(f["phrase"]) > 2], key=len, reverse=True)
        l_phrases = sorted([f["phrase"] for f in legit_feats if len(f["phrase"]) > 2], key=len, reverse=True)

        for phrase in p_phrases:
            pattern = re.compile(rf"\b({re.escape(phrase)})\b", re.IGNORECASE)
            safe_text = pattern.sub(
                r'<mark class="xai-phish" title="Phishing Indicator (+Influence)">\1</mark>',
                safe_text
            )

        for phrase in l_phrases:
            pattern = re.compile(rf"\b({re.escape(phrase)})\b", re.IGNORECASE)
            safe_text = pattern.sub(
                r'<mark class="xai-legit" title="Legitimate Indicator (-Influence)">\1</mark>',
                safe_text
            )

        return safe_text

    def get_global_top_features(self, top_n: int = 25) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Returns top global features with highest positive weights (Phishing)
        and most negative weights (Legitimate).
        """
        lr = self.models.get("logistic_regression")
        if lr is None or not hasattr(lr, "coef_") or self.feature_names is None:
            return [], []

        coef = lr.coef_[0]
        sorted_indices = np.argsort(coef)

        # Most negative = Legitimate
        legit_indices = sorted_indices[:top_n]
        legit_list = [
            {
                "rank": i + 1,
                "feature": str(self.feature_names[idx]),
                "weight": round(float(coef[idx]), 4),
                "direction": "Legitimate Anchor"
            }
            for i, idx in enumerate(legit_indices)
        ]

        # Most positive = Phishing
        phish_indices = sorted_indices[-top_n:][::-1]
        phish_list = [
            {
                "rank": i + 1,
                "feature": str(self.feature_names[idx]),
                "weight": round(float(coef[idx]), 4),
                "direction": "Phishing Trigger"
            }
            for i, idx in enumerate(phish_indices)
        ]

        return phish_list, legit_list

if __name__ == "__main__":
    explainer = ThreatExplainer()
    print("Explainer ready:", explainer.is_ready())
    res = explainer.explain("Urgent! Your bank account has been suspended. Click here to verify your password immediately.")
    print("Explain result:", res["prediction"], res["risk_score_percent"], "%")
    print("Phishing indicators:", [f["phrase"] for f in res["top_phishing_indicators"][:5]])
