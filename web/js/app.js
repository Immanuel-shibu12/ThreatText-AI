/**
 * ThreatText AI - Streamlined Client-Side Controller
 * Focused exclusively on:
 * 1. Single email threat scanning with Explainable AI (XAI) review
 * 2. Bulk CSV batch screening and export
 */

document.addEventListener("DOMContentLoaded", () => {
    initModeToggle();
    initPresets();
    initSingleEmailAnalyzer();
    initBatchAnalysis();
    fetchSystemStatus();
});

// =============================================================================
// 1. Mode Switcher (Single Email Scanner vs Batch CSV Scanner)
// =============================================================================
function initModeToggle() {
    const btnSingle = document.getElementById("btn-mode-single");
    const btnBatch = document.getElementById("btn-mode-batch");
    const sectionSingle = document.getElementById("section-single");
    const sectionBatch = document.getElementById("section-batch");

    if (btnSingle && btnBatch) {
        btnSingle.addEventListener("click", () => {
            btnSingle.classList.add("active");
            btnBatch.classList.remove("active");
            sectionSingle.style.display = "block";
            sectionBatch.style.display = "none";
        });

        btnBatch.addEventListener("click", () => {
            btnBatch.classList.add("active");
            btnSingle.classList.remove("active");
            sectionBatch.style.display = "block";
            sectionSingle.style.display = "none";
        });
    }
}

// =============================================================================
// 2. Telemetry Status
// =============================================================================
async function fetchSystemStatus() {
    try {
        const res = await fetch("/api/status");
        if (res.ok) {
            const data = await res.json();
            const pill = document.getElementById("server-status-pill");
            if (pill) {
                pill.innerHTML = `<span class="status-dot"></span> ML Online (${data.total_samples || '17,512'} emails, 98.17% Acc)`;
            }
        }
    } catch (e) {
        console.warn("Could not fetch server status:", e);
    }
}

// =============================================================================
// 3. 1-Click Demo Scenarios
// =============================================================================
let DEMO_PRESETS = [];

async function initPresets() {
    try {
        const res = await fetch("/api/samples");
        if (res.ok) {
            DEMO_PRESETS = await res.json();
            renderPresetChips();
        }
    } catch (e) {
        console.warn("Could not load presets:", e);
    }
}

function renderPresetChips() {
    const container = document.getElementById("presets-container");
    if (!container) return;
    container.innerHTML = "";

    DEMO_PRESETS.forEach(preset => {
        const chip = document.createElement("button");
        chip.className = "preset-chip";
        // Clean scenario title without spoiler badges (No Legitimate / Phishing badges)
        chip.innerHTML = `<span>⚡ ${preset.title}</span>`;
        chip.title = `Click to load and automatically analyze: ${preset.title}`;
        chip.addEventListener("click", () => {
            // Highlight active scenario chip
            document.querySelectorAll(".preset-chip").forEach(c => c.classList.remove("active"));
            chip.classList.add("active");

            document.getElementById("email-subject").value = preset.subject || "";
            document.getElementById("email-body").value = preset.body || "";
            // Automatically analyze and display output immediately
            analyzeEmail();
        });
        container.appendChild(chip);
    });
}

// =============================================================================
// 4. Single Email Analyzer & Explainable Review
// =============================================================================
function initSingleEmailAnalyzer() {
    const btnAnalyze = document.getElementById("btn-analyze");
    const btnClear = document.getElementById("btn-clear");
    const fileInput = document.getElementById("email-file-input");

    if (btnAnalyze) {
        btnAnalyze.addEventListener("click", () => analyzeEmail());
    }

    if (btnClear) {
        btnClear.addEventListener("click", () => {
            document.getElementById("email-subject").value = "";
            document.getElementById("email-body").value = "";
            const resultBox = document.getElementById("analysis-result-container");
            if (resultBox) resultBox.style.display = "none";
        });
    }

    if (fileInput) {
        fileInput.addEventListener("change", (e) => {
            if (e.target.files.length > 0) {
                handleEmailFileUpload(e.target.files[0]);
            }
        });
    }
}

async function handleEmailFileUpload(file) {
    const formData = new FormData();
    formData.append("file", file);

    const btnAnalyze = document.getElementById("btn-analyze");
    if (btnAnalyze) {
        btnAnalyze.disabled = true;
        btnAnalyze.innerHTML = `<span>â³ Reading ${file.name}...</span>`;
    }

    try {
        const res = await fetch("/api/upload", {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        if (data.error) {
            alert(`File Error: ${data.error}`);
            return;
        }

        if (data.subject) document.getElementById("email-subject").value = data.subject;
        if (data.body) document.getElementById("email-body").value = data.body;

        renderAnalysisResult(data);
    } catch (e) {
        alert(`Failed to parse email file: ${e.message}`);
    } finally {
        if (btnAnalyze) {
            btnAnalyze.disabled = false;
            btnAnalyze.innerHTML = `<span>ðŸ” Scan Email & Generate Review</span>`;
        }
    }
}

async function analyzeEmail() {
    const subject = document.getElementById("email-subject").value;
    const body = document.getElementById("email-body").value;
    const modelSelect = document.getElementById("model-select");
    const modelName = modelSelect ? modelSelect.value : "logistic_regression";

    if (!body.trim()) {
        alert("Please enter or paste email content before analyzing.");
        return;
    }

    const btnAnalyze = document.getElementById("btn-analyze");
    if (btnAnalyze) {
        btnAnalyze.disabled = true;
        btnAnalyze.innerHTML = `<span>â³ Evaluating Email via NLP Pipeline...</span>`;
    }

    try {
        const res = await fetch("/api/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                subject: subject,
                body: body,
                model: modelName
            })
        });

        const data = await res.json();
        if (data.error) {
            alert(`Analysis Error: ${data.error}`);
            return;
        }

        renderAnalysisResult(data);
    } catch (e) {
        alert(`Error communicating with NLP backend: ${e.message}`);
    } finally {
        if (btnAnalyze) {
            btnAnalyze.disabled = false;
            btnAnalyze.innerHTML = `<span>ðŸ” Scan Email & Generate Review</span>`;
        }
    }
}

function renderAnalysisResult(data) {
    const container = document.getElementById("analysis-result-container");
    if (!container) return;
    container.style.display = "block";

    // Smooth scroll down to review
    container.scrollIntoView({ behavior: "smooth", block: "start" });

    // Verdict Banner
    const banner = document.getElementById("threat-banner");
    const badge = document.getElementById("verdict-badge");
    const summaryText = document.getElementById("threat-summary-text");
    const scoreVal = document.getElementById("risk-score-value");
    const progressFill = document.getElementById("risk-progress-fill");

    const riskScore = data.risk_score_percent ?? (data.risk_score_pct || 0);
    const threatLevel = data.threat_level || "Unknown";
    const isPhish = data.prediction === "Phishing";

    if (banner) {
        banner.className = "threat-banner " + (riskScore >= 75 ? "critical" : (riskScore >= 50 ? "suspicious" : "safe"));
    }
    if (badge) {
        badge.className = "verdict-badge " + (riskScore >= 75 ? "critical" : (riskScore >= 50 ? "suspicious" : "safe"));
        badge.textContent = threatLevel;
    }
    if (summaryText) {
        summaryText.textContent = isPhish ? "Deceptive Phishing Attempt Detected" : "Legitimate Normal Correspondence";
    }
    if (scoreVal) {
        scoreVal.textContent = `${riskScore}%`;
        scoreVal.style.color = data.threat_badge_color || "#38bdf8";
    }
    if (progressFill) {
        progressFill.style.width = `${riskScore}%`;
        progressFill.style.backgroundColor = data.threat_badge_color || "#38bdf8";
    }

    // Highlighted Text Box
    const emailBox = document.getElementById("xai-highlighted-content");
    if (emailBox) {
        emailBox.innerHTML = data.highlighted_html || escapeHtml(data.cleaned_text || "");
    }

    // Top Phishing Indicators
    const phishContainer = document.getElementById("top-phishing-tokens");
    if (phishContainer) {
        phishContainer.innerHTML = "";
        const phishList = data.top_phishing_indicators || [];
        if (phishList.length === 0) {
            phishContainer.innerHTML = `<div class="token-row" style="color: var(--text-muted);">No significant phishing triggers detected.</div>`;
        } else {
            phishList.slice(0, 6).forEach(item => {
                const row = document.createElement("div");
                row.className = "token-row";
                row.innerHTML = `
                    <span class="token-phrase" style="color: #fca5a5;">âš ï¸ ${escapeHtml(item.phrase)}</span>
                    <span class="token-score positive">+${item.influence}</span>
                `;
                phishContainer.appendChild(row);
            });
        }
    }

    // Top Legitimate Anchors
    const legitContainer = document.getElementById("top-legitimate-tokens");
    if (legitContainer) {
        legitContainer.innerHTML = "";
        const legitList = data.top_legitimate_indicators || [];
        if (legitList.length === 0) {
            legitContainer.innerHTML = `<div class="token-row" style="color: var(--text-muted);">No distinct legitimate anchors found.</div>`;
        } else {
            legitList.slice(0, 6).forEach(item => {
                const row = document.createElement("div");
                row.className = "token-row";
                row.innerHTML = `
                    <span class="token-phrase" style="color: #86efac;">ðŸ›¡ï¸ ${escapeHtml(item.phrase)}</span>
                    <span class="token-score negative">-${item.influence}</span>
                `;
                legitContainer.appendChild(row);
            });
        }
    }

    // Recommendations List
    const recsList = document.getElementById("recommendations-list");
    if (recsList) {
        recsList.innerHTML = "";
        (data.recommendations || []).forEach(rec => {
            const li = document.createElement("li");
            li.style.marginBottom = "0.5rem";
            li.textContent = rec;
            recsList.appendChild(li);
        });
    }

    // Security Disclaimer
    const disclaimerBox = document.getElementById("threat-disclaimer");
    if (disclaimerBox && data.disclaimer) {
        disclaimerBox.textContent = data.disclaimer;
    }
}

// =============================================================================
// 5. Batch CSV Screening
// =============================================================================
let currentBatchEnrichedCsv = null;

function initBatchAnalysis() {
    const btnLoadSample = document.getElementById("btn-load-sample-batch");
    const fileInput = document.getElementById("batch-file-input");
    const dropZone = document.getElementById("batch-drop-zone");
    const btnRunBatch = document.getElementById("btn-run-batch");
    const btnDownloadCsv = document.getElementById("btn-download-batch-csv");

    if (btnLoadSample) {
        btnLoadSample.addEventListener("click", async () => {
            try {
                const res = await fetch("/data/sample_batch.csv");
                if (res.ok) {
                    const text = await res.text();
                    document.getElementById("batch-csv-textarea").value = text;
                    runBatchAnalysis(text);
                }
            } catch (e) {
                alert(`Could not load sample CSV: ${e.message}`);
            }
        });
    }

    if (btnRunBatch) {
        btnRunBatch.addEventListener("click", () => {
            const csvContent = document.getElementById("batch-csv-textarea").value;
            if (!csvContent.trim()) {
                alert("Please paste CSV data or upload a CSV file first.");
                return;
            }
            runBatchAnalysis(csvContent);
        });
    }

    if (fileInput) {
        fileInput.addEventListener("change", (e) => {
            if (e.target.files.length > 0) {
                readCsvFile(e.target.files[0]);
            }
        });
    }

    if (dropZone) {
        dropZone.addEventListener("click", () => fileInput && fileInput.click());
        dropZone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropZone.classList.add("dragover");
        });
        dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
        dropZone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropZone.classList.remove("dragover");
            if (e.dataTransfer.files.length > 0) {
                readCsvFile(e.dataTransfer.files[0]);
            }
        });
    }

    if (btnDownloadCsv) {
        btnDownloadCsv.addEventListener("click", () => {
            if (!currentBatchEnrichedCsv) {
                alert("No batch results available to download.");
                return;
            }
            const blob = new Blob([currentBatchEnrichedCsv], { type: "text/csv;charset=utf-8;" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `ThreatText_Batch_Predictions_${new Date().toISOString().slice(0, 10)}.csv`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        });
    }
}

function readCsvFile(file) {
    const reader = new FileReader();
    reader.onload = (e) => {
        const text = e.target.result;
        document.getElementById("batch-csv-textarea").value = text;
        runBatchAnalysis(text);
    };
    reader.readAsText(file);
}

async function runBatchAnalysis(csvContent) {
    const btnRunBatch = document.getElementById("btn-run-batch");
    const modelSelect = document.getElementById("batch-model-select");
    const modelName = modelSelect ? modelSelect.value : "logistic_regression";

    if (btnRunBatch) {
        btnRunBatch.disabled = true;
        btnRunBatch.innerHTML = `<span>â³ Scanning Batch Emails...</span>`;
    }

    try {
        const res = await fetch("/api/batch", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                csv_data: csvContent,
                model: modelName
            })
        });

        const data = await res.json();
        if (data.error) {
            alert(`Batch Error: ${data.error}`);
            return;
        }

        renderBatchResults(data);
    } catch (e) {
        alert(`Failed to run batch analysis: ${e.message}`);
    } finally {
        if (btnRunBatch) {
            btnRunBatch.disabled = false;
            btnRunBatch.innerHTML = `<span>ðŸš€ Run Bulk Batch Review</span>`;
        }
    }
}

function renderBatchResults(data) {
    currentBatchEnrichedCsv = data.enriched_csv;
    const container = document.getElementById("batch-results-container");
    if (!container) return;
    container.style.display = "block";

    document.getElementById("batch-stat-total").textContent = data.total_analyzed;
    document.getElementById("batch-stat-phish").textContent = `${data.phishing_detected} (${data.phishing_percentage}%)`;
    document.getElementById("batch-stat-legit").textContent = data.legitimate_detected;
    document.getElementById("batch-text-col").textContent = data.text_column_detected;

    const tbody = document.getElementById("batch-table-body");
    if (tbody) {
        tbody.innerHTML = "";
        (data.rows || []).forEach(row => {
            const tr = document.createElement("tr");
            const isPhish = row.prediction === "Phishing";
            tr.innerHTML = `
                <td style="font-family: var(--font-mono);">${row.row_id}</td>
                <td style="font-size: 0.85rem; color: var(--text-muted); max-width: 420px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${escapeHtml(row.snippet)}</td>
                <td>
                    <span class="preset-badge ${isPhish ? 'phish' : 'legit'}" style="font-size: 0.8rem; font-weight: 700;">
                        ${row.prediction}
                    </span>
                </td>
                <td style="font-family: var(--font-mono); font-weight: 700; color: ${isPhish ? '#f87171' : '#34d399'};">
                    ${row.risk_score_pct}%
                </td>
                <td style="font-size: 0.825rem; font-weight: 600;">${row.threat_level}</td>
            `;
            tbody.appendChild(tr);
        });
    }

    container.scrollIntoView({ behavior: "smooth", block: "start" });
}

// Utility: HTML Escaping
function escapeHtml(text) {
    if (!text) return "";
    const map = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
    };
    return text.toString().replace(/[&<>"']/g, m => map[m]);
}
