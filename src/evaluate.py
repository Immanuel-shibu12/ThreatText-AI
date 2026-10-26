"""
ThreatText AI - Evaluation & Performance Analysis Module
Generates high-resolution confusion matrix visualizations, ROC curves,
error analysis breakdown (False Positives vs False Negatives),
and model comparison charts across all 3 supervised classifiers.
"""

import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend safe for server/background execution
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    roc_curve,
    auc,
    precision_recall_curve
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")

os.makedirs(RESULTS_DIR, exist_ok=True)

def run_evaluation_suite():
    print("=" * 65)
    print("       ThreatText AI - Comprehensive Model Evaluation Suite      ")
    print("=" * 65)

    test_set_path = os.path.join(MODELS_DIR, "test_set.joblib")
    lr_path = os.path.join(MODELS_DIR, "phishing_model.joblib")
    nb_path = os.path.join(MODELS_DIR, "naive_bayes_model.joblib")
    svm_path = os.path.join(MODELS_DIR, "linear_svm_model.joblib")
    vec_path = os.path.join(MODELS_DIR, "tfidf_vectorizer.joblib")

    if not (os.path.exists(test_set_path) and os.path.exists(lr_path) and os.path.exists(vec_path)):
        raise FileNotFoundError("Missing trained model artifacts. Please run train.py first.")

    print("\n[1/5] Loading test data and trained models...")
    test_data = joblib.load(test_set_path)
    lr_model = joblib.load(lr_path)
    nb_model = joblib.load(nb_path) if os.path.exists(nb_path) else None
    svm_model = joblib.load(svm_path) if os.path.exists(svm_path) else None
    tfidf = joblib.load(vec_path)

    X_test_raw = test_data["X_test_raw"]
    y_test = np.array(test_data["y_test"])
    original_text = test_data["original_text"]

    X_test_vec = tfidf.transform(X_test_raw)

    # Primary model (Logistic Regression) evaluation
    y_pred_lr = lr_model.predict(X_test_vec)
    y_proba_lr = lr_model.predict_proba(X_test_vec)[:, 1]

    print("\n[2/5] Detailed Classification Report (Logistic Regression):")
    report_dict = classification_report(
        y_test, y_pred_lr, target_names=["Legitimate (0)", "Phishing (1)"], output_dict=True
    )
    print(classification_report(y_test, y_pred_lr, target_names=["Legitimate (0)", "Phishing (1)"]))

    # Save classification report json
    with open(os.path.join(RESULTS_DIR, "classification_report.json"), "w") as f:
        json.dump(report_dict, f, indent=2)

    # 1. Confusion Matrix Plot (High Resolution)
    print("\n[3/5] Generating high-resolution Confusion Matrix visualization...")
    cm = confusion_matrix(y_test, y_pred_lr)
    tn, fp, fn, tp = cm.ravel()

    fig, ax = plt.subplots(figsize=(7, 6), dpi=300)
    
    # Custom color palette: deep blue/teal tones
    cmap = sns.light_palette("#1e3a8a", as_cmap=True)
    
    group_names = ["True Legitimate (TN)", "False Phishing (FP)", "Missed Phishing (FN)", "Detected Phishing (TP)"]
    group_counts = [f"{value:,}" for value in cm.flatten()]
    group_percentages = [f"{value:.2%}" for value in cm.flatten() / np.sum(cm)]
    labels = [f"{v1}\n{v2}\n({v3})" for v1, v2, v3 in zip(group_names, group_counts, group_percentages)]
    labels = np.asarray(labels).reshape(2, 2)

    sns.heatmap(
        cm, annot=labels, fmt="", cmap=cmap, cbar=True,
        xticklabels=["Predicted Legitimate", "Predicted Phishing"],
        yticklabels=["Actual Legitimate", "Actual Phishing"],
        linewidths=1.5, linecolor="#f1f5f9", ax=ax
    )
    ax.set_title("ThreatText AI - Primary Model Confusion Matrix\n(Held-Out Test Set, N = " + f"{len(y_test):,})", fontsize=12, fontweight="bold", pad=15)
    ax.set_ylabel("Actual Email Ground Truth", fontsize=11, fontweight="semibold")
    ax.set_xlabel("ThreatText AI Prediction", fontsize=11, fontweight="semibold")
    plt.tight_layout()

    cm_output_path = os.path.join(RESULTS_DIR, "confusion_matrix.png")
    plt.savefig(cm_output_path, dpi=300)
    plt.close()
    print(f"Confusion matrix saved to: {cm_output_path}")

    # 2. Model Comparison Bar Chart
    comp_csv = os.path.join(RESULTS_DIR, "model_comparison.csv")
    if os.path.exists(comp_csv):
        print("\n[4/5] Generating Model Comparison Bar Chart...")
        comp_df = pd.read_csv(comp_csv)
        metrics = ["Accuracy", "Precision", "Recall", "F1-Score"]
        x = np.arange(len(comp_df))
        width = 0.18
        colors = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6"]

        fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
        for i, metric in enumerate(metrics):
            vals = comp_df[metric].values * 100
            rects = ax.bar(x + (i - 1.5) * width, vals, width, label=metric, color=colors[i], alpha=0.9)
            for rect in rects:
                height = rect.get_height()
                ax.annotate(f"{height:.1f}%",
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=7.5, fontweight='bold')

        ax.set_ylabel("Score (%)", fontsize=11, fontweight="semibold")
        ax.set_title("ThreatText AI - Multi-Model Benchmark Comparison on Held-Out Test Set", fontsize=12, fontweight="bold", pad=15)
        ax.set_xticks(x)
        ax.set_xticklabels(comp_df["Model"], fontsize=10, fontweight="semibold")
        ax.set_ylim(80, 103)
        ax.legend(loc="lower right", frameon=True)
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        plt.tight_layout()
        
        comp_plot_path = os.path.join(RESULTS_DIR, "model_comparison_bar.png")
        plt.savefig(comp_plot_path, dpi=300)
        plt.close()
        print(f"Model comparison chart saved to: {comp_plot_path}")

    # 3. ROC Curves Comparison Plot
    print("\n[5/5] Generating Multi-Model ROC Curves...")
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    
    # Logistic Regression
    fpr_lr, tpr_lr, _ = roc_curve(y_test, y_proba_lr)
    auc_lr = auc(fpr_lr, tpr_lr)
    ax.plot(fpr_lr, tpr_lr, color="#3b82f6", lw=2.2, label=f"Logistic Regression (AUC = {auc_lr:.4f})")

    # Linear SVM (Calibrated)
    if svm_model is not None:
        if hasattr(svm_model, "predict_proba"):
            y_proba_svm = svm_model.predict_proba(X_test_vec)[:, 1]
        else:
            dec = svm_model.decision_function(X_test_vec)
            y_proba_svm = 1.0 / (1.0 + np.exp(-dec))
        fpr_svm, tpr_svm, _ = roc_curve(y_test, y_proba_svm)
        auc_svm = auc(fpr_svm, tpr_svm)
        ax.plot(fpr_svm, tpr_svm, color="#10b981", lw=2.2, linestyle="--", label=f"Linear SVM (AUC = {auc_svm:.4f})")

    # Multinomial Naive Bayes
    if nb_model is not None:
        y_proba_nb = nb_model.predict_proba(X_test_vec)[:, 1]
        fpr_nb, tpr_nb, _ = roc_curve(y_test, y_proba_nb)
        auc_nb = auc(fpr_nb, tpr_nb)
        ax.plot(fpr_nb, tpr_nb, color="#f59e0b", lw=2.2, linestyle="-.", label=f"Multinomial Naive Bayes (AUC = {auc_nb:.4f})")

    ax.plot([0, 1], [0, 1], color="#94a3b8", lw=1.5, linestyle=":", label="Random Guess (AUC = 0.5000)")
    ax.set_xlim([-0.01, 1.0])
    ax.set_ylim([0.0, 1.02])
    ax.set_xlabel("False Positive Rate (1 - Specificity)", fontsize=11, fontweight="semibold")
    ax.set_ylabel("True Positive Rate (Sensitivity / Recall)", fontsize=11, fontweight="semibold")
    ax.set_title("ThreatText AI - Receiver Operating Characteristic (ROC) Curves\n(Held-Out Test Set, N = " + f"{len(y_test):,})", fontsize=12, fontweight="bold", pad=15)
    ax.legend(loc="lower right", frameon=True, fontsize=9.5)
    ax.grid(True, linestyle="--", alpha=0.3)
    plt.tight_layout()

    roc_output_path = os.path.join(RESULTS_DIR, "roc_curves.png")
    plt.savefig(roc_output_path, dpi=300)
    plt.close()
    print(f"ROC Curves plot saved to: {roc_output_path}")

    # 4. False Positives & False Negatives Error Analysis
    print("\nExtracting False Positives & False Negatives for error diagnosis...")
    error_records = []
    for idx in range(len(y_test)):
        actual = y_test[idx]
        pred = y_pred_lr[idx]
        prob = y_proba_lr[idx]
        text_snip = original_text[idx][:300]
        
        if actual != pred:
            err_type = "False Positive (Legitimate classified as Phishing)" if pred == 1 else "False Negative (Phishing classified as Legitimate)"
            error_records.append({
                "Test_Index": idx,
                "Actual_Label": "Legitimate" if actual == 0 else "Phishing",
                "Predicted_Label": "Phishing" if pred == 1 else "Legitimate",
                "Phishing_Probability": round(prob, 4),
                "Error_Type": err_type,
                "Email_Snippet": text_snip
            })

    error_df = pd.DataFrame(error_records)
    error_csv_path = os.path.join(RESULTS_DIR, "error_analysis.csv")
    error_df.to_csv(error_csv_path, index=False)
    print(f"Extracted {len(error_df)} misclassified emails for error analysis (saved to {error_csv_path}).")
    print(f"  - False Positives: {fp} emails ({fp / (tn + fp):.2%} of legitimate)")
    print(f"  - False Negatives: {fn} emails ({fn / (fn + tp):.2%} of phishing)")
    print("=" * 65)

if __name__ == "__main__":
    run_evaluation_suite()
