@echo off
title ThreatText AI - Model Training & Evaluation Suite
echo =====================================================================
echo    ThreatText AI: Multi-Model Retraining and Evaluation Pipeline
echo =====================================================================
echo.
echo [Step 1/2] Training Logistic Regression, Linear SVM, and Naive Bayes...
python src/train.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Training failed! Please check traceback above.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [Step 2/2] Generating Confusion Matrix, ROC Curves, and Error Analysis...
python src/evaluate.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Evaluation suite failed!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo =====================================================================
echo [SUCCESS] Training & Evaluation Pipeline Completed!
echo Benchmark metrics and high-res visualizations updated in results/
echo =====================================================================
echo.
pause
