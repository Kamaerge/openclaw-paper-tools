@echo off
set "OPENCLAW_CHANNEL=feishu"
set "OPENCLAW_TARGET=oc_c10dddb79f789d945e7d2317d5014d08"
set "OPENCLAW_BIN=openclaw"
set "PYTHON_BIN=python"
set "HF_DAILY_INTERESTS=AR/Gaze,Prediction"
set "HF_DAILY_GEN_KEYWORDS=AR,eye tracking,gaze stabilization,augmented reality"
set "HF_DAILY_EFF_KEYWORDS=temporal prediction,trajectory prediction,motion forecasting,sequence prediction"
set AUTO_SUBMIT_TOPN=1
set USE_NANOPDF_ANALYZER=1
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
pwsh -NoProfile -ExecutionPolicy Bypass -File D:\Project\openclaw-paper-tools\skills\hf-daily-papers\run_and_send.ps1
