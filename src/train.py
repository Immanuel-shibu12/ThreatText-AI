"""
ThreatText AI - Model Training and Comparison Pipeline
Fits TF-IDF (unigrams + bigrams) on training data only.
Trains and compares Multinomial Naive Bayes, Logistic Regression, and Linear SVM.
Saves models, vectorizer, and evaluation benchmarks.
"""

import os
import sys
import json
import time
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix
)

# Import local preprocessing
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.preprocessing import clean_email_text

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "emails.csv")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

def train_and_evaluate_pipeline():
    print("=" * 65)
    print("       ThreatText AI - Machine Learning Training Pipeline        ")
    print("=" * 65)

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}. Run download_and_prep_data.py first.")

    t0 = time.time()
    print(f"\n[1/5] Loading cleaned dataset from: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    print(f"Total rows: {len(df)}")
    print("Class distribution:")
    print(df["label_name"].value_counts())

    # Preprocessing
    print("\n[2/5] Applying NLP preprocessing (HTML stripping, URL tokens, normalization)...")
    df["processed_text"] = df["text"].astype(str).apply(clean_email_text)
    
    # Filter out empty strings after preprocessing if any
    df = df[df["processed_text"].str.len() > 5].copy()
    print(f"Dataset size after preprocessing filter: {len(df)}")

    # Stratified Train-Test Split (80% train, 20% test)
    print("\n[3/5] Performing Stratified Train-Test Split (80% Train, 20% Held-Out Test)...")
    X = df["processed_text"]
    y = df["label"].values

    X_train_raw, X_test_raw, y_train, y_test, indices_train, indices_test = train_test_split(
        X, y, df.index.values, test_size=0.20, random_state=42, stratify=y
    )

    print(f"Training set: {len(X_train_raw)} samples (Phishing: {np.sum(y_train==1)}, Legitimate: {np.sum(y_train==0)})")
    print(f"Held-out test set: {len(X_test_raw)} samples (Phishing: {np.sum(y_test==1)}, Legitimate: {np.sum(y_test==0)})")

    # Fit TF-IDF on training set only (avoid data leakage)
    print("\n[4/5] Fitting TF-IDF Vectorizer on training data (Unigram + Bigram, max_features=8000)...")
    tfidf = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=8000,
        min_df=3,
        sublinear_tf=True,
        stop_words="english"
    )

    X_train_vec = tfidf.fit_transform(X_train_raw)
    X_test_vec = tfidf.transform(X_test_raw)
    print(f"TF-IDF matrix shape: {X_train_vec.shape}")

    # Train Candidates
    models = {
        "Multinomial Naive Bayes": MultinomialNB(alpha=0.1),
        "Logistic Regression": LogisticRegression(
            C=2.0, max_iter=1000, random_state=42, class_weight="balanced"
        ),
        "Linear SVM": CalibratedClassifierCV(
            LinearSVC(C=1.0, random_state=42, class_weight="balanced", max_iter=2000),
            cv=3
        )
    }

    comparison_records = []
    trained_models = {}

    print("\n[5/5] Training and evaluating supervised models on held-out test set:")
    for name, model in models.items():
        m_start = time.time()
        print(f"\n  -> Training {name}...")
        model.fit(X_train_vec, y_train)
        train_duration = time.time() - m_start

        # Inference on held-out test
        y_pred = model.predict(X_test_vec)
        
        # Probabilities
        if hasattr(model, "predict_proba"):
            y_proba = model.predict_proba(X_test_vec)[:, 1]
            auc = roc_auc_score(y_test, y_proba)
        elif hasattr(model, "decision_function"):
            y_scores = model.decision_function(X_test_vec)
            auc = roc_auc_score(y_test, y_scores)
        else:
            auc = 0.0

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, pos_label=1)
        rec = recall_score(y_test, y_pred, pos_label=1)
        f1 = f1_score(y_test, y_pred, pos_label=1)
        cm = confusion_matrix(y_test, y_pred)

        print(f"     Accuracy : {acc * 100:.2f}%")
        print(f"     Precision: {prec * 100:.2f}% (Phishing)")
        print(f"     Recall   : {rec * 100:.2f}% (Phishing detection rate)")
        print(f"     F1-Score : {f1 * 100:.2f}%")
        print(f"     ROC-AUC  : {auc:.4f}")
        print(f"     Confusion Matrix: TN={cm[0,0]}, FP={cm[0,1]}, FN={cm[1,0]}, TP={cm[1,1]}")

        comparison_records.append({
            "Model": name,
            "Accuracy": round(acc, 4),
            "Precision": round(prec, 4),
            "Recall": round(rec, 4),
            "F1-Score": round(f1, 4),
            "ROC-AUC": round(auc, 4),
            "Train Time (s)": round(train_duration, 3),
            "True Negative": int(cm[0, 0]),
            "False Positive": int(cm[0, 1]),
            "False Negative": int(cm[1, 0]),
            "True Positive": int(cm[1, 1])
        })
        trained_models[name] = model

    # Save comparison table
    comparison_df = pd.DataFrame(comparison_records)
    comparison_csv_path = os.path.join(RESULTS_DIR, "model_comparison.csv")
    comparison_df.to_csv(comparison_csv_path, index=False)
    print(f"\nComparison table saved to: {comparison_csv_path}")

    # Primary explainable model: Logistic Regression
    primary_model = trained_models["Logistic Regression"]
    primary_model_path = os.path.join(MODELS_DIR, "phishing_model.joblib")
    joblib.dump(primary_model, primary_model_path)
    print(f"Primary model (Logistic Regression) saved to: {primary_model_path}")

    # Vectorizer
    vectorizer_path = os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib")
    joblib.dump(tfidf, vectorizer_path)
    print(f"Fitted TF-IDF vectorizer saved to: {vectorizer_path}")

    # Save additional candidate models for dynamic evaluation
    joblib.dump(trained_models["Multinomial Naive Bayes"], os.path.join(MODELS_DIR, "naive_bayes_model.joblib"))
    joblib.dump(trained_models["Linear SVM"], os.path.join(MODELS_DIR, "linear_svm_model.joblib"))

    # Save test set for reproducible evaluation dashboard
    test_data = {
        "X_test_raw": X_test_raw.tolist(),
        "y_test": y_test.tolist(),
        "indices_test": indices_test.tolist(),
        "original_text": df.loc[indices_test, "text"].tolist()
    }
    test_set_path = os.path.join(MODELS_DIR, "test_set.joblib")
    joblib.dump(test_data, test_set_path)
    print(f"Held-out test set saved to: {test_set_path}")

    # Save summary metadata
    meta = {
        "total_samples": len(df),
        "legitimate_samples": int(np.sum(df["label"] == 0)),
        "phishing_samples": int(np.sum(df["label"] == 1)),
        "train_samples": len(X_train_raw),
        "test_samples": len(X_test_raw),
        "vocabulary_size": len(tfidf.vocabulary_),
        "selected_model": "Logistic Regression",
        "training_timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    with open(os.path.join(RESULTS_DIR, "training_meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    total_time = time.time() - t0
    print(f"\nEntire training & evaluation completed in {total_time:.2f} seconds.")
    print("=" * 65)

if __name__ == "__main__":
    train_and_evaluate_pipeline()
