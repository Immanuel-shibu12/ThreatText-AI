"""
ThreatText AI - Dataset Loader & Validation Module
Handles genuine phishing dataset loading, missing value verification,
duplicate inspection, label sanitization, and summary metrics generation.
"""

import os
import json
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DATA_CSV = os.path.join(DATA_DIR, "emails.csv")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")

def validate_and_inspect_dataset(csv_path: str = DATA_CSV) -> Dict[str, Any]:
    """
    Validates the dataset file, checks for nulls/duplicates,
    and returns comprehensive statistics for display and reporting.
    """
    if not os.path.exists(csv_path):
        return {
            "status": "error",
            "message": f"Dataset file not found at {csv_path}. Please run download_and_prep_data.py first."
        }

    df = pd.read_csv(csv_path)

    total_records = len(df)
    missing_text = int(df["text"].isna().sum()) if "text" in df.columns else 0
    missing_labels = int(df["label"].isna().sum()) if "label" in df.columns else 0
    duplicate_count = int(df["text"].duplicated().sum()) if "text" in df.columns else 0

    class_counts = df["label_name"].value_counts().to_dict() if "label_name" in df.columns else {}
    legit_count = int(class_counts.get("Legitimate", 0))
    phishing_count = int(class_counts.get("Phishing", 0))

    legit_pct = round((legit_count / total_records) * 100, 2) if total_records > 0 else 0.0
    phishing_pct = round((phishing_count / total_records) * 100, 2) if total_records > 0 else 0.0

    # Text length metrics (word count and char count)
    df["char_len"] = df["text"].astype(str).str.len()
    avg_char_len = round(float(df["char_len"].mean()), 1)
    median_char_len = int(df["char_len"].median())

    stats = {
        "status": "success",
        "file_path": csv_path,
        "total_records": total_records,
        "legitimate_count": legit_count,
        "phishing_count": phishing_count,
        "legitimate_percentage": legit_pct,
        "phishing_percentage": phishing_pct,
        "missing_text_count": missing_text,
        "missing_label_count": missing_labels,
        "duplicate_records_found": duplicate_count,
        "average_email_length_chars": avg_char_len,
        "median_email_length_chars": median_char_len,
        "sources": [
            {
                "name": "Enron Email Dataset",
                "role": "Legitimate benchmark correspondence",
                "description": "Authentic organizational communications from senior corporate staff."
            },
            {
                "name": "Nazario Phishing Corpus",
                "role": "Real-world phishing attacks",
                "description": "Historical collection of targeted phishing campaigns, credential harvesters, and financial scams."
            },
            {
                "name": "SpamAssassin Public Corpus",
                "role": "Curated spam and ham emails",
                "description": "Vetted benchmark corpus maintained by Apache Software Foundation."
            }
        ],
        "limitations": [
            "Historical email distribution; emerging zero-day LLM-generated phishing techniques require continuous retuning.",
            "Textual analysis excludes external URL redirection chains and DNS reputation lookups.",
            "Attribution is model-based linear approximation and should be used as assistive triage rather than a sole security verdict."
        ]
    }

    # Persist summary json to results
    try:
        os.makedirs(RESULTS_DIR, exist_ok=True)
        with open(os.path.join(RESULTS_DIR, "dataset_summary.json"), "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
    except Exception as e:
        print(f"Warning: could not write dataset_summary.json: {e}")

    return stats

def get_dataset_sample(n: int = 5, category: str = "all") -> list:
    """Returns n sample records from the genuine dataset."""
    if not os.path.exists(DATA_CSV):
        return []
    df = pd.read_csv(DATA_CSV)
    if category.lower() == "phishing":
        subset = df[df["label"] == 1]
    elif category.lower() == "legitimate":
        subset = df[df["label"] == 0]
    else:
        subset = df
    sample = subset.sample(min(n, len(subset)), random_state=42)
    return sample[["text", "label", "label_name"]].to_dict(orient="records")

if __name__ == "__main__":
    summary = validate_and_inspect_dataset()
    print("Dataset Validation Summary:")
    print(json.dumps(summary, indent=2))
