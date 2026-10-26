/**
 * ThreatText AI - Client-Side Controller
 * 1. Animated Vector Robot Welcome Page
 * 2. 1-Click Benchmark Test Scenarios
 * 3. Single Email Threat Scanning & Explainable AI (XAI)
 * 4. Bulk CSV Batch Screening & CSV Export
 */

document.addEventListener("DOMContentLoaded", () => {
    initModeToggle();
    initWelcomeRobo();
    initPresets();
    initSingleEmailAnalyzer();
    initBatchAnalysis();
    fetchSystemStatus();
});

// =============================================================================
// 1. Mode Switcher (Welcome -> Single Email Scanner -> Batch CSV Scanner)
// =============================================================================
function initModeToggle() {
    const btnWelcome = document.getElementById("btn-mode-welcome");
    const btnSingle = document.getElementById("btn-mode-single");
    const btnBatch = document.getElementById("btn-mode-batch");
    const sectionWelcome = document.getElementById("section-welcome");
    const sectionSingle = document.getElementById("section-single");
    const sectionBatch = document.getElementById("section-batch");
    const btnEnterDash = document.getElementById("btn-enter-threattext-dash");
    const brandLogo = document.querySelector(".brand-wrapper");

    function showMode(mode) {
        if (btnWelcome) btnWelcome.classList.toggle("active", mode === "welcome");
        if (btnSingle) btnSingle.classList.toggle("active", mode === "single");
        if (btnBatch) btnBatch.classList.toggle("active", mode === "batch");

        if (sectionWelcome) sectionWelcome.style.display = (mode === "welcome" ? "block" : "none");
        if (sectionSingle) sectionSingle.style.display = (mode === "single" ? "block" : "none");
        if (sectionBatch) sectionBatch.style.display = (mode === "batch" ? "block" : "none");

        window.scrollTo({ top: 0, behavior: "smooth" });
    }

    if (btnWelcome) {
        btnWelcome.addEventListener("click", () => showMode("welcome"));
    }
    if (btnSingle) {
        btnSingle.addEventListener("click", () => showMode("single"));
    }
    if (btnBatch) {
        btnBatch.addEventListener("click", () => showMode("batch"));
    }
    if (btnEnterDash) {
        btnEnterDash.addEventListener("click", () => {
            showMode("single");
        });
    }
    if (brandLogo) {
        brandLogo.style.cursor = "pointer";
        brandLogo.addEventListener("click", () => showMode("welcome"));
    }

    // Direct entry via URL hash (e.g. #scanner, #dashboard, or #website enters directly)
    if (window.location.hash === "#scanner" || window.location.hash === "#dashboard" || window.location.hash === "#website") {
        showMode("single");
    } else if (window.location.hash === "#batch") {
        showMode("batch");
    }
}

// =============================================================================
// 2. Welcome Robot Controller
// =============================================================================
function initWelcomeRobo() {
    const btnAnimated = document.getElementById("btn-mode-animated");
    const btnRender = document.getElementById("btn-mode-render");
    const stageAnimated = document.getElementById("animated-robot-stage");
    const stageRender = document.getElementById("render-robot-stage");

    if (btnAnimated && btnRender) {
        btnAnimated.addEventListener("click", () => {
            btnAnimated.classList.add("active");
            btnRender.classList.remove("active");
            if (stageAnimated) stageAnimated.style.display = "block";
            if (stageRender) stageRender.style.display = "none";
        });
        btnRender.addEventListener("click", () => {
            btnRender.classList.add("active");
            btnAnimated.classList.remove("active");
            if (stageAnimated) stageAnimated.style.display = "none";
            if (stageRender) stageRender.style.display = "block";
        });
    }

    const btnWave = document.getElementById("btn-trigger-wave");
    const btnWink = document.getElementById("btn-trigger-wink");
    const btnJump = document.getElementById("btn-trigger-jump");
    const wavingArm = document.getElementById("robot-waving-arm");
    const eyeLeft = document.getElementById("eye-left-group");
    const roboStage = document.getElementById("animated-robot-stage");
    const robotFigure = document.getElementById("robot-figure");
    const speechHeadline = document.getElementById("speech-headline");
    const speechBody = document.getElementById("speech-body-text");

    function triggerRoboWave() {
        if (wavingArm) {
            wavingArm.classList.add("waving-active");
            wavingArm.style.animation = "none";
            void wavingArm.offsetWidth;
            wavingArm.style.animation = "waveArmGestureFast 0.7s ease-in-out 4";
        }
        setTimeout(() => {
            if (wavingArm) {
                wavingArm.classList.remove("waving-active");
                wavingArm.style.animation = "";
            }
        }, 2800);
    }

    if (btnWave) {
        btnWave.addEventListener("click", triggerRoboWave);
    }

    if (robotFigure) {
        robotFigure.addEventListener("click", triggerRoboWave);
    }

    if (btnWink && eyeLeft) {
        btnWink.addEventListener("click", () => {
            eyeLeft.style.transform = "scaleY(0.1)";
            eyeLeft.style.transition = "transform 0.15s ease";
            setTimeout(() => {
                eyeLeft.style.transform = "scaleY(1)";
            }, 350);
        });
    }

    if (btnJump && roboStage) {
        btnJump.addEventListener("click", () => {
            roboStage.style.transform = "translateY(-24px)";
            roboStage.style.transition = "transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1)";
            setTimeout(() => {
                roboStage.style.transform = "translateY(0)";
            }, 400);
        });
    }
}

// =============================================================================
// 3. Telemetry Status
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
// 4. 1-Click Benchmark Test Scenarios
// =============================================================================
const DEFAULT_PRESETS = [
    {
        "id": "bank_verification",
        "title": "Bank Account Urgent Suspension",
        "type": "Phishing",
        "subject": "URGENT: Temporary Suspension on Online Banking Access",
        "sender": "Chase Security Alerts <service-notice@chase-secure-verify.net>",
        "body": "Dear Valued Customer,\n\nWe have detected multiple unauthorized login attempts to your online banking portal from an unrecognized IP address (194.26.29.112).\n\nFor your security, access to your funds and bill payment features has been temporarily suspended.\n\nTo restore your access immediately and avoid permanent account lock within 24 hours, you must verify your identity and confirm your account password using our secure verification server:\n\nhttp://chase-identity-auth-portal.com/login?verify=true&session=89327498234\n\nFailure to verify within 24 hours will result in permanent suspension and a $50 administrative fee."
    },
    {
        "id": "college_timetable",
        "title": "College Class Schedule & Timetable",
        "type": "Legitimate",
        "subject": "Updated Lecture Timetable for Fall Semester - CS Dept",
        "sender": "Dr. Sarah Jenkins <sjenkins@university.edu>",
        "body": "Dear Computer Science Students,\n\nPlease find attached the revised lecture timetable for the upcoming Fall semester. Due to classroom renovations in Hall B, Natural Language Processing (CS 460) will now be held in Room 304.\n\nOffice hours schedule:\n- Tuesday: 2:00 PM - 4:00 PM\n- Thursday: 10:00 AM - 12:00 PM\n\nPlease review the syllabus on the campus portal and let me know if you have timetable conflicts.\n\nBest regards,\nDr. Sarah Jenkins\nDepartment of Computer Science & Engineering"
    },
    {
        "id": "delivery_credentials",
        "title": "Delivery Notification & Parcel Update",
        "type": "Phishing",
        "subject": "Notice: Incomplete Delivery Address for Parcel #DHL-984210",
        "sender": "DHL Express Notification <tracking-update@dhl-parcel-redelivery.org>",
        "body": "Important Notice from DHL Courier Services:\n\nYour incoming international package (#DHL-984210-US) could not be delivered on scheduled date because the recipient address format is incomplete.\n\nA small customs processing charge of $2.99 is required to reschedule redelivery to your door.\n\nClick here to confirm your street address and pay fee securely:\nhttp://192.168.1.88/dhl-package-update/verify\n\nIf unpaid within 48 hours, package will be returned to sender overseas."
    },
    {
        "id": "hr_payroll_update",
        "title": "HR Payroll Direct Deposit Update",
        "type": "Phishing",
        "subject": "Action Required: Update Your Direct Deposit Bank Account Details",
        "sender": "Corporate HR Portal <hr-support@internal-benefits-update.cc>",
        "body": "Hello Employee,\n\nDuring routine quarterly auditing, we noticed your direct deposit bank routing number requires re-validation for the upcoming salary disbursement cycle.\n\nPlease confirm your banking password and account details immediately on the employee portal:\nhttp://portal-login-benefits.com/auth\n\nFailure to update by 5:00 PM will cause your payroll disbursement to be deferred."
    },
    {
        "id": "workplace_meeting",
        "title": "Workplace Project Review & Agenda",
        "type": "Legitimate",
        "subject": "Agenda: ThreatText AI Architecture Review - Tomorrow 10:00 AM",
        "sender": "Alex Rivera <alex.rivera@enterprise.com>",
        "body": "Hi Team,\n\nHere is the finalized agenda for our architecture review tomorrow:\n\n1. Overview of 17,512 email benchmark dataset and sanitation metrics\n2. TF-IDF unigram and bigram feature representations\n3. Evaluation of Logistic Regression, Linear SVM, and Naive Bayes on held-out test split\n4. Review of XAI signed feature attribution engine\n5. Q&A and next sprint timeline\n\nThe slide deck is uploaded to the internal drive. See you all tomorrow!\n\nAlex"
    }
];

let DEMO_PRESETS = DEFAULT_PRESETS;

function initPresets() {
    renderPresetChips();

    fetch("/api/samples")
        .then(res => {
            if (res.ok) return res.json();
            throw new Error("HTTP error " + res.status);
        })
        .then(data => {
            if (Array.isArray(data) && data.length > 0) {
                DEMO_PRESETS = data;
                renderPresetChips();
            }
        })
        .catch(err => {
            console.log("Using default demo scenarios.");
        });
}

function renderPresetChips() {
    const container = document.getElementById("presets-container");
    if (!container) return;
    container.innerHTML = "";

    DEMO_PRESETS.forEach(preset => {
        const chip = document.createElement("button");
        chip.className = "preset-chip";
        chip.innerHTML = `<span class="chip-indicator"></span><span>${escapeHtml(preset.title)}</span>`;
        chip.title = `Click to load: ${preset.title}`;
        chip.addEventListener("click", () => {
            document.querySelectorAll(".preset-chip").forEach(c => c.classList.remove("active"));
            chip.classList.add("active");

            document.getElementById("email-subject").value = preset.subject || "";
            document.getElementById("email-body").value = preset.body || "";
            analyzeEmail();
        });
        container.appendChild(chip);
    });
}

// =============================================================================
// 5. Single Email Analyzer & Explainable Review
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
            document.querySelectorAll(".preset-chip").forEach(c => c.classList.remove("active"));
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
        btnAnalyze.innerHTML = `<span>Reading ${escapeHtml(file.name)}...</span>`;
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
            btnAnalyze.innerHTML = `<span>Scan Email & Generate Review</span>`;
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
        btnAnalyze.innerHTML = `<span>Evaluating Email via NLP Pipeline...</span>`;
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
            btnAnalyze.innerHTML = `<span>Scan Email & Generate Review</span>`;
        }
    }
}

function renderAnalysisResult(data) {
    const container = document.getElementById("analysis-result-container");
    if (!container) return;
    container.style.display = "block";

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
                    <span class="token-phrase" style="color: #fca5a5;">${escapeHtml(item.phrase)}</span>
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
                    <span class="token-phrase" style="color: #86efac;">${escapeHtml(item.phrase)}</span>
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
// 6. Batch CSV Screening
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
        btnRunBatch.innerHTML = `<span>Scanning Batch Emails...</span>`;
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
            btnRunBatch.innerHTML = `<span>Run Bulk Batch Review</span>`;
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

// =============================================================================
// Utility: HTML Escaping
// =============================================================================
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
