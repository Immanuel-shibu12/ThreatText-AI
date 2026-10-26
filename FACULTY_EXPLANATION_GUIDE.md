# 🎓 ThreatText AI — Faculty Presentation & Defense Guide
### 25-Mark College Project Defense & Viva Cheat-Sheet

---

## ⚡ 1. Two-Minute Elevator Pitch to Faculty
> *"Respected Faculty, our project is **ThreatText AI**, an explainable NLP-based phishing email detection system. While conventional email filters rely on rigid keyword rules or opaque deep-learning 'black-boxes' that security analysts cannot audit, ThreatText AI uses domain-aware Natural Language Processing and Supervised Machine Learning to achieve **98.17% accuracy** on a verified benchmark corpus of **17,512 real-world emails**.*
>
> *Crucially, we solve the 'black-box' barrier through **Signed Feature Attribution ($x_i \cdot w_i$)**: for every email, our system highlights the exact words pushing the score toward Phishing (in red) and legitimate anchors (in green), accompanied by actionable cybersecurity advice and zero external API dependencies."*

---

## 📋 2. How to Map the Project to the 5 Rubric Criteria (25 Marks)

### Criterion 1: Problem Statement & Dataset (5 Marks)
- **Problem**: Phishing causes over 85% of corporate cyber breaches. Security Operations Center (SOC) analysts cannot safely quarantine executive emails without knowing *why* a model flagged them.
- **Dataset**: Curated from 3 premier public archives:
  1. **Enron Corpus**: Authentic organizational business correspondence (Legitimate).
  2. **Nazario Corpus**: Real-world targeted phishing attacks and credential harvesters.
  3. **SpamAssassin Public Corpus**: Apache-vetted legitimate and phishing emails.
- **Data Hygiene**: Total **17,512 verified emails** (10,976 Legitimate [62.7%], 6,536 Phishing [37.3%]).
  - **0 Nulls** (16 corrupted records dropped).
  - **0 Duplicates** (577 duplicate emails identified and removed to prevent memorization).
  - Clean separation: Synthetic demo samples (`data/sample_batch.csv`) are strictly segregated from training data.

### Criterion 2: Preprocessing & Feature Extraction (5 Marks)
- **Domain-Aware Text Cleaning** (`src/preprocessing.py`):
  1. *HTML Tag Stripping*: Strips tags while inserting spaces so words don't coalesce (e.g., `Urgent</p><p>Verify` becomes `Urgent Verify`, not `UrgentVerify`).
  2. *URL & IP Normalization*: Normalizes IP links (`http://192.168.1.1`) to `ip_url_link`, HTTP to `http_url_token`, and HTTPS to `secure_url_token`.
  3. *Negation Retention*: Strictly preserves words like *"not"*, *"no"*, and *"never"* so semantic context isn't inverted.
- **TF-IDF with Unigrams and Bigrams**:
  - Extracts single words (*"password"*, *"urgent"*) and two-word pairs (*"verify account"*, *"click here"*).
  - **Zero Data Leakage**: Fitted strictly on the 80% training partition (`X_train`); test partition (`X_test`) is processed using `transform()` only.

### Criterion 3: Supervised Model Implementation (5 Marks)
- Implemented and evaluated **3 Supervised Classifiers** (`src/train.py`):
  1. **Logistic Regression (Primary XAI)**: 98.17% Accuracy, 97.63% Recall, 0.9982 ROC-AUC.
  2. **Calibrated Linear SVM**: 98.32% Accuracy, 97.09% Recall, 0.9984 ROC-AUC.
  3. **Multinomial Naive Bayes**: 97.09% Accuracy, 94.41% Recall, 0.9963 ROC-AUC.
- **Reproducible Split**: Stratified 80/20 train/test partition with fixed `random_state=42`.
- Models, vectorizer, and test set saved as portable `.joblib` artifacts.

### Criterion 4: Performance Evaluation & Live Demo (5 Marks)
- **Held-Out Test Results** ($N = 3,503$ emails):
  - True Legitimate (TN): 2,163 | Detected Phishing (TP): 1,276
  - False Phishing (FP): 33 | Missed Phishing (FN): 31
  - Phishing Precision: 97.48% | Phishing Recall: 97.63%
- **Evaluation Charts Generated**:
  - `results/confusion_matrix.png`
  - `results/model_comparison_bar.png`
  - `results/roc_curves.png`
- **Application Capabilities**:
  - Pasted text analysis & RFC 822 `.eml`/`.txt` file parsing.
  - Bulk CSV batch screening & downloadable enriched predictions.
  - Prominent disclaimer: *"Probabilistic NLP feature attribution for triage assistance; not a definitive cryptographic verdict."*

### Criterion 5: Project Report & Documentation (5 Marks)
- Complete technical report at `results/PROJECT_REPORT.md` (and embedded in the web dashboard's "Project Report" tab).
- 25-mark rubric compliance matrix, methodology diagrams, screenshot guidance, references, and viva Q&A.

---

## 💡 3. The Explainable AI (XAI) Formula
Faculty will ask: *"How does your model explain its decisions?"*

Explain this formula:
$$\text{Contribution}_j = x_j \cdot w_j$$

- $x_j$: The TF-IDF importance of token $j$ in the input email.
- $w_j$: The model coefficient (weight) learned during training.
- **Positive Contribution ($+w_j$)**: Pushes the prediction toward **Phishing** (e.g. *account*, *verify*, *password*, *urgent*, *click here*). Highlighted in **Red**.
- **Negative Contribution ($-w_j$)**: Pushes the prediction toward **Legitimate** (e.g. *meeting*, *agenda*, *attached*, *schedule*, *university*). Highlighted in **Green**.

Calibrated Risk Score:
$$P(\text{Phishing} \mid \mathbf{x}) = \frac{1}{1 + e^{-(\beta_0 + \sum x_j w_j)}}$$

---

## 🗂️ 4. Quick Tour of the Project Folder
- `app.py`: Pure Python HTTP server (running on port 8000, zero Flask/Streamlit).
- `start.bat`: 1-Click launcher that starts the server and opens the website.
- `train.bat`: 1-Click script to retrain all models and update charts.
- `web/`: Contains `index.html`, `style.css`, and `app.js` (responsive dark cybersecurity dashboard).
- `data/`: Contains `emails.csv` (17,512 verified emails) and `sample_batch.csv`.
- `models/`: Trained model binaries (`.joblib`).
- `results/`: Confusion matrix, ROC curves, comparison charts, and project report.
- `tests/`: 27 automated unit tests (`python -m unittest discover tests`).
