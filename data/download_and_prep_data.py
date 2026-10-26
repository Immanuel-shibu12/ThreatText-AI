"""
ThreatText AI - Dataset Download & Preparation Script
Downloads the canonical benchmark phishing email corpus (Enron + Nazario + SpamAssassin),
cleans duplicates, handles missing values, standardizes labels, and exports data/emails.csv.
"""

import os
import sys
import time
import urllib.request
import pandas as pd
import numpy as np

DATA_URL = "https://huggingface.co/datasets/zefang-liu/phishing-email-dataset/resolve/main/Phishing_Email.csv"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "emails.csv")
RAW_CSV = os.path.join(OUTPUT_DIR, "raw_phishing_email.csv")

def download_file(url, target_path):
    print(f"Downloading dataset from: {url}")
    print(f"Target location: {target_path}")
    t0 = time.time()
    
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as resp, open(target_path, "wb") as out_file:
        total_size = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        chunk_size = 1024 * 1024 # 1MB
        
        while True:
            chunk = resp.read(chunk_size)
            if not chunk:
                break
            out_file.write(chunk)
            downloaded += len(chunk)
            if total_size > 0:
                percent = (downloaded / total_size) * 100
                print(f"Progress: {downloaded / (1024*1024):.1f}MB / {total_size / (1024*1024):.1f}MB ({percent:.1f}%)", end="\r")
            else:
                print(f"Downloaded: {downloaded / (1024*1024):.1f}MB", end="\r")
                
    elapsed = time.time() - t0
    print(f"\nDownload completed successfully in {elapsed:.2f} seconds.")

def prepare_dataset(raw_path, output_path):
    print("Loading raw CSV...")
    df = pd.read_csv(raw_path)
    print(f"Raw shape: {df.shape}")
    print(f"Raw columns: {df.columns.tolist()}")

    # Find the text and type columns
    text_col = None
    type_col = None
    for c in df.columns:
        c_lower = c.strip().lower()
        if "text" in c_lower or "email" in c_lower and "type" not in c_lower:
            text_col = c
        if "type" in c_lower or "label" in c_lower:
            type_col = c
            
    if text_col is None or type_col is None:
        raise ValueError(f"Could not automatically detect columns. Found: {df.columns}")

    print(f"Using text column: '{text_col}', label column: '{type_col}'")

    # Drop missing
    initial_len = len(df)
    df = df.dropna(subset=[text_col, type_col])
    print(f"Dropped {initial_len - len(df)} rows with NaN values.")

    # Standardize labels: 1 for Phishing, 0 for Legitimate (Safe)
    def map_label(val):
        s = str(val).strip().lower()
        if "phish" in s or s == "1" or s == "true" or "spam" in s:
            return 1
        return 0

    df["label"] = df[type_col].apply(map_label)
    df["label_name"] = df["label"].map({1: "Phishing", 0: "Legitimate"})
    df["text"] = df[text_col].astype(str).str.strip()

    # Filter out empty or extremely short artifacts (< 15 characters)
    df = df[df["text"].str.len() >= 15]

    # Deduplicate based on text to prevent train-test contamination
    dedup_before = len(df)
    df = df.drop_duplicates(subset=["text"])
    print(f"Deduplication removed {dedup_before - len(df)} duplicate emails.")

    # Select clean columns
    final_df = df[["text", "label", "label_name"]].copy()

    # Reset index
    final_df.reset_index(drop=True, inplace=True)

    print("\n--- Final Dataset Summary ---")
    print(f"Total instances: {len(final_df)}")
    print(final_df["label_name"].value_counts(normalize=False))
    print("\nProportions:")
    print(final_df["label_name"].value_counts(normalize=True).round(4) * 100)

    final_df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\nSaved clean emails dataset to: {output_path}")

    # Remove raw file if desired to save space
    if os.path.exists(raw_path):
        os.remove(raw_path)
        print("Cleaned up raw temporary download.")

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_CSV):
        download_file(DATA_URL, RAW_CSV)
        prepare_dataset(RAW_CSV, OUTPUT_CSV)
    else:
        print(f"Dataset already exists at: {OUTPUT_CSV}")
        df = pd.read_csv(OUTPUT_CSV)
        print(f"Shape: {df.shape}")
        print(df["label_name"].value_counts())
