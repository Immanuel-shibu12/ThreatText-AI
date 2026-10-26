# ThreatText AI: An Explainable NLP-Based Phishing Email Detection System Using Machine Learning

**Academic Project Report**  
*Course: Natural Language Processing & Applied Machine Learning*  
*Total Evaluation Marks: 25 Marks*  
*Candidate Submission Document*

---

## Abstract

Phishing remains the primary vector for cyberattacks, credential theft, and corporate network intrusion. While conventional email filters rely on rigid keyword heuristics or opaque black-box machine learning models, modern security operations demand transparent, interpretable decisions to audit false alarms and justify defensive actions. This project presents **ThreatText AI**, an explainable Natural Language Processing (NLP) framework and interactive web application for phishing email classification. 

Using a curated and deduplicated corpus of 17,512 verified emails from the Enron, Nazario, and SpamAssassin archives, we implement a domain-aware preprocessing pipeline that cleans HTML markup, normalizes URLs and IP addresses into structured indicator tokens, and preserves critical negation semantics. Features are represented using Term Frequency-Inverse Document Frequency (TF-IDF) spanning unigrams and bigrams ($N$-gram range 1–2, 8,000 features). Three supervised machine learning models—Multinomial Naive Bayes, Logistic Regression, and Linear Support Vector Machines (SVM)—were trained and evaluated on an identical, held-out test split of 3,503 emails without data leakage. 

Empirical experiments demonstrated that Calibrated Linear SVM achieved the highest overall accuracy (**98.32%**), while Logistic Regression achieved the superior phishing recall rate (**97.63%**, $F_1 = 97.55\%$, $\text{ROC-AUC} = 0.9982$). Crucially, ThreatText AI integrates model-based signed linear feature attribution ($x_i \cdot w_i$), providing token-level visual explanations that highlight predictive phrases in real time, accompanied by actionable security countermeasures. A production-ready Streamlit application provides demonstration benchmarks, raw text evaluation, and RFC 822 `.eml`/`.txt` file parsing.

---

## 1. Introduction & Motivation

Phishing attacks manipulate human psychology—exploiting urgency, fear, authority, and financial anxiety—to induce recipients into disclosing credentials, authorizing illegitimate financial transactions, or installing malware. According to industry threat intelligence reports, over 85% of cybersecurity breaches originate via malicious email communications.

Although modern spam filters successfully intercept mass promotional solicitations, targeted phishing messages increasingly imitate legitimate institutional communications (e.g., banking security notices, college administration announcements, parcel delivery updates). Detecting such threats requires deep textual scrutiny of nuanced syntactic and semantic cues.

Moreover, enterprise cybersecurity adoption faces the "black-box barrier." Security Operations Center (SOC) analysts cannot safely quarantine critical communications or block executive workflows based on unexplained model probabilities. Explainable Artificial Intelligence (XAI) is therefore not merely an academic desideratum, but an operational prerequisite.

ThreatText AI addresses this dual challenge by coupling high-performance NLP classification with transparent token attribution.

---

## 2. Problem Statement & Project Objectives

### 2.1 Problem Statement
Identifying phishing messages manually is inefficient and error-prone due to deceptive linguistic spoofing. Traditional keyword matching fails against lexical modifications, while complex deep learning systems lack interpretability and incur substantial computational overhead. There is a need for an NLP-based detection system that:
1. Accurately distinguishes phishing from legitimate messages.
2. Formulates feature representations that preserve security semantics.
3. Quantifies empirical performance across diverse supervised classifiers.
4. Explains individual predictions by identifying the specific tokens that influenced classification.

### 2.2 Project Objectives
1. **Dataset Curation:** Acquire, inspect, clean, deduplicate, and analyze a labeled dataset of real-world phishing and legitimate emails.
2. **Preprocessing Pipeline:** Implement domain-aware text cleaning, URL/email tokenization, HTML stripping, and negation preservation.
3. **Feature Engineering:** Build a leak-free TF-IDF vectorization engine extracting unigram and bigram patterns.
4. **Model Comparison:** Train and compare Multinomial Naive Bayes, Logistic Regression, and Linear SVM on identical held-out test data.
5. **Explainability Architecture:** Design signed feature attribution algorithms to render token-level interpretability.
6. **Web Prototype:** Deploy an interactive, modern Streamlit web application supporting demo scenarios, manual input, and file uploads.
7. **Rigorous Evaluation:** Quantify accuracy, precision, recall, $F_1$-score, confusion matrix metrics, and perform false positive/negative error analysis.

---

## 3. Dataset Collection & Exploratory Data Analysis

### 3.1 Data Sources
The project utilizes a consolidated corpus synthesizing:
- **Enron Email Corpus:** Legitimate corporate correspondence reflecting natural organizational communications.
- **Nazario Phishing Corpus:** Documented, real-world phishing attacks spanning credential harvesting and social engineering.
- **SpamAssassin Public Corpus:** Hand-classified legitimate and spam/phishing examples.

### 3.2 Data Cleaning & Sanitization
Prior to training, data hygiene protocols were applied:
1. **Missing Value Removal:** Dropped all records with null text or label attributes (16 rows).
2. **Text Normalization Filter:** Discarded corrupted fragments with fewer than 15 characters.
3. **Deduplication:** Removed 577 duplicate emails across the combined archives. Deduplicating prior to splitting is vital to prevent nearly identical emails from appearing in both training and test partitions, which would otherwise inflate evaluation metrics.

### 3.3 Final Class Distribution
The cleaned dataset contains **17,512 unique emails**:

| Class Label | Category | Count | Percentage |
| :---: | :---: | :---: | :---: |
| **0** | Legitimate Email | 10,976 | 62.68% |
| **1** | Phishing Email | 6,536 | 37.32% |
| **Total** | — | **17,512** | **100.00%** |

```
Distribution Visualization:
[============================= Legitimate: 62.7% =============================][============== Phishing: 37.3% ==============]
```

---

## 4. NLP Methodology & Preprocessing Pipeline

### 4.1 Domain-Aware Preprocessing
Standard NLP pipelines routinely strip all punctuation, numbers, and links, discarding vital cybersecurity signals. ThreatText AI introduces a domain-aware pipeline:

1. **HTML Parsing & Entity Unescaping:** Strips `<script>`, `<style>`, and HTML formatting tags while converting break/paragraph tags into spaces, preventing words from inadvertently coalescing (e.g., `word1</p><p>word2` $\rightarrow$ `word1 word2`).
2. **URL & IP Address Normalization:**
   - Raw IP URLs (e.g., `http://192.168.1.1/login`) are normalized to `ip_url_link`.
   - Insecure HTTP URLs are replaced with `http_url_token`.
   - Secure HTTPS URLs are replaced with `secure_url_token`.
   - Email addresses are mapped to `email_address_token`.
3. **Negation Retention:** Standard stop-word removal often discards words like "not", "no", and "never", which invert phrase semantics. Our pipeline retains negations to maintain context.
4. **Punctuation & Urgency Normalization:** Repeated exclamation points (e.g., `!!!!`) and question marks are compressed into canonical tokens (`!!`, `??`) to capture emotional manipulation.
5. **Casing & Whitespace:** Converted to consistent lowercase with single-space normalization.

### 4.2 Feature Representation: TF-IDF with N-Grams
Text is vectorized using Term Frequency-Inverse Document Frequency:

$$\text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \log\left(\frac{1 + |D|}{1 + |\{d \in D : t \in d\}|}\right) + 1$$

To capture multi-word manipulative patterns (e.g., *"verify account"*, *"password reset"*, *"immediate action"*), we configure:
- **$N$-Gram Range:** $(1, 2)$ — includes both unigrams and contiguous bigrams.
- **Vocabulary Size:** 8,000 most informative features (`max_features=8000`).
- **Sublinear TF:** Logarithmic term frequency scaling ($\text{sublinear\_tf}=\text{True}$) to dampen the impact of excessively repetitive words.
- **Minimum Document Frequency:** `min_df=3` to filter one-off typos.
- **Data-Leakage Prevention:** The vectorizer is strictly fitted on `X_train` (`fit_transform`) and subsequently applied to `X_test` (`transform`).

---

## 5. Machine Learning Models & Implementation

We compare three complementary supervised learning algorithms:

### 5.1 Multinomial Naive Bayes (MNB)
A generative probabilistic baseline grounded in Bayes' theorem with the conditional independence assumption:

$$P(y = c \mid \mathbf{x}) \propto P(y = c) \prod_{j=1}^{d} P(x_j \mid y = c)$$

Laplace smoothing ($\alpha = 0.1$) is incorporated to prevent zero-probability penalties for unseen features. MNB provides near-instantaneous training ($0.052\text{s}$) and serves as a strong text classification benchmark.

### 5.2 Logistic Regression (Primary Explainable Model)
A discriminative linear model predicting the posterior probability via the sigmoid function:

$$P(y = 1 \mid \mathbf{x}) = \sigma(z) = \frac{1}{1 + e^{-z}}, \quad z = \beta_0 + \sum_{j=1}^{d} \beta_j x_j$$

Trained using the L-BFGS solver with balanced class weighting and $L_2$ regularization ($C = 2.0$). Logistic Regression was chosen as the primary deployment model because its learned coefficients ($\beta_j$) map directly to feature log-odds, enabling exact, closed-form explainability.

### 5.3 Linear Support Vector Machine (Linear SVM)
A maximum-margin hyperplane classifier seeking to maximize the geometric margin between phishing and legitimate feature representations:

$$\min_{\mathbf{w}, b, \xi} \frac{1}{2}\|\mathbf{w}\|^2 + C \sum_{i=1}^{n} \xi_i \quad \text{s.t.} \quad y_i(\mathbf{w}^T \mathbf{x}_i + b) \ge 1 - \xi_i, \quad \xi_i \ge 0$$

Calibrated via Platt scaling (3-fold cross-validation) to produce valid posterior probability estimates for risk thresholding.

---

## 6. Explainable AI (XAI) Formulation

ThreatText AI provides **local token-level attribution** based on the linear model's signed feature weights:

$$\text{Contribution}_j = x_j \cdot \beta_j$$

- When $\text{Contribution}_j > 0$: The token pushed the prediction toward **Phishing** ($+z$).
- When $\text{Contribution}_j < 0$: The token pushed the prediction toward **Legitimate** ($-z$).

### Token Highlighting & Color Coding
The web interface maps these local contributions into visual highlights:
- **Red Span (`#fee2e2` / `#ef4444` border):** Malicious indicators (e.g., *verify*, *account*, *suspended*, *click*, *http_url_token*).
- **Green Span (`#dcfce7` / `#10b981` border):** Legitimate anchors (e.g., *attached*, *schedule*, *meeting*, *university*, *project*).

Hovering over any marked token displays its exact numerical weight ($\beta_j$) and local influence score ($x_j \beta_j$).

---

## 7. Experimental Results & Performance Evaluation

All models were evaluated on the **identical held-out test split of 3,503 emails** (2,196 Legitimate, 1,307 Phishing).

### 7.1 Empirical Model Benchmark Comparison

| Model Architecture | Test Accuracy | Precision (Phishing) | Recall (Phishing) | $F_1$-Score | ROC-AUC | Training Time |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Multinomial Naive Bayes** | 97.09% | 97.70% | 94.41% | 96.03% | 0.9963 | 0.052 s |
| **Logistic Regression (Selected)** | **98.17%** | **97.48%** | **97.63%** | **97.55%** | **0.9982** | **0.466 s** |
| **Linear SVM (Calibrated)** | 98.32% | 98.37% | 97.09% | 97.73% | 0.9984 | 0.771 s |

### 7.2 Confusion Matrix Breakdown (Primary Model)

```
                       Predicted Legitimate    Predicted Phishing
Actual Legitimate             2,163 (TN)               33 (FP)
Actual Phishing                  31 (FN)            1,276 (TP)
```

- **True Negatives (TN = 2,163):** Legitimate emails accurately allowed through.
- **True Positives (TP = 1,276):** Phishing attacks accurately intercepted (**97.63% detection rate**).
- **False Positives (FP = 33):** Legitimate emails mistakenly flagged ($1.50\%$ false alarm rate).
- **False Negatives (FN = 31):** Phishing emails that evaded detection ($2.37\%$ miss rate).

### 7.3 Detailed Class-Wise Metrics

```
                precision    recall  f1-score   support

Legitimate (0)       0.99      0.98      0.99      2,196
  Phishing (1)       0.97      0.98      0.98      1,307

      accuracy                           0.98      3,503
     macro avg       0.98      0.98      0.98      3,503
  weighted avg       0.98      0.98      0.98      3,503
```

### 7.4 Security Trade-Off Analysis: Precision vs. Recall
In spam filtering, high precision is prioritized so users do not lose important correspondence. However, in **phishing detection, recall is the paramount security metric**. A false negative (missed phishing email) exposes an employee to credential harvesting or malware deployment, leading to potentially catastrophic enterprise compromise. 

Logistic Regression was chosen because it achieved the highest phishing recall (**97.63%**), capturing 1,276 out of 1,307 threats while sustaining an exceptional precision of 97.48%.

---

## 8. Error Diagnosis & Qualitative Analysis

We conducted an in-depth inspection of the 64 misclassified emails from the test set (`results/error_analysis.csv`):

### 8.1 False Positives (33 Cases)
- **Root Cause:** Routine business emails containing security-adjacent vocabulary (e.g., *"Please reset your corporate VPN password per IT policy"* or vendor notices containing numerous external links).
- **Remediation:** Incorporating sender domain reputation checks and DKIM signature verification to establish organizational legitimacy before applying text models.

### 8.2 False Negatives (31 Cases)
- **Root Cause:** Sophisticated spear-phishing messages using concise, polite wording with minimal text (e.g., *"Hi Mark, please review the attached invoice when free."*). Without explicit urgency or credential keywords, the text alone lacks strong positive $\beta$ signals.
- **Remediation:** Multimodal integration that scans linked landing page HTML and inspects attachment payloads.

---

## 9. Web Application Interface & User Experience

The ThreatText AI application was implemented in Python using **Streamlit** with a custom dark-mode cybersecurity theme:

1. **Page 1 — Overview Dashboard:** Executive summary, KPI telemetry cards, class distribution pie chart, and end-to-end pipeline architecture.
2. **Page 2 — Email Risk Analyzer:** Interactive analysis interface featuring:
   - Preset demonstration benchmarks (Banking verification, College timetable, Delivery notice, Sprint meeting, HR payroll).
   - Custom subject and body input fields.
   - RFC 822 `.eml` and `.txt` file uploader with automated header/body parsing.
   - Visual Threat Level Badge (Critical, Suspicious, Low, Safe) and progress meter.
   - Tabbed explainability explorer with highlighted text, influence bar charts, and security advice.
3. **Page 3 — Model Performance & Benchmarks:** Interactive comparison tables, high-resolution confusion matrix heatmaps, multi-metric bar charts, and downloadable error datasets.
4. **Page 4 — Explainability Explorer:** Global corpus feature rankings (Top 25 positive vs negative words) and mathematical walkthroughs.
5. **Page 5 — Academic Assessment Guide:** Complete 25-mark rubric compliance tables, high-yield viva Q&A notes, and architectural summaries.

---

## 10. System Limitations & Future Scope

### 10.1 Limitations
1. **Textual Scope:** The current implementation analyzes email headers and body text; it does not execute binary attachments (e.g., `.exe`, macro-enabled `.docm`).
2. **Homoglyph & Zero-Width Obfuscation:** Attackers using Cyrillic characters that mimic Latin letters (e.g., substituting 'а' for 'a') can degrade exact n-gram matching.
3. **Zero-Day Phishing Narratives:** Phishing campaigns utilizing novel social engineering themes absent from historical training corpora may be underweighted.

### 10.2 Future Improvements
- **Subword Tokenization (BPE/WordPiece):** Integrating Byte-Pair Encoding to counteract adversarial character perturbations.
- **DKIM/SPF Header Authentication:** Direct verification of cryptographic domain keys to eliminate impersonation.
- **URL Sandbox Crawler:** Headless browser integration to dynamically analyze the final landing page destination.

---

## 11. Conclusion

ThreatText AI successfully demonstrates that domain-aware NLP preprocessing coupled with linear supervised classifiers delivers state-of-the-art phishing detection (**98.17% accuracy, 97.63% recall**) while providing complete, mathematical explainability. By replacing opaque black-box outputs with token-level attribution and actionable security recommendations, ThreatText AI bridges the gap between machine learning research and real-world cybersecurity operations.

---

## 12. References

1. Blanzieri, E., & Bryl, A. (2008). A survey of learning-based techniques of email spam filtering. *Artificial Intelligence Review*, 29(1), 63-92.
2. Sahingoz, O. K., Buber, E., Demir, O., & Diri, B. (2019). Machine learning based phishing detection from URLs. *Expert Systems with Applications*, 117, 345-357.
3. Nazario, J. (2005). Phishing Corpus: A collection of real phishing emails. *Monkey.org Phishing Archive*.
4. Klimt, B., & Yang, Y. (2004). The Enron corpus: A new dataset for email classification research. *European Conference on Machine Learning*, 217-226.
5. Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). "Why should I trust you?": Explaining the predictions of any classifier. *ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, 1135-1144.
6. Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, 2825-2830.
