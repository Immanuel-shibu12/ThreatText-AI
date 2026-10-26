@echo off
title ThreatText AI - Explainable Phishing Detection Server
echo =====================================================================
echo    ThreatText AI: Explainable NLP Phishing Detection System
echo =====================================================================
echo.
echo Launching local server at: http://127.0.0.1:8000
echo Dataset: 17,512 verified emails (Enron + Nazario + SpamAssassin)
echo Supervised ML: Logistic Regression, Linear SVM, Naive Bayes
echo.
echo Press Ctrl+C in this terminal window to stop the server.
echo.

start "" "http://127.0.0.1:8000"
python app.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Server exited with error code %ERRORLEVEL%.
    pause
)
