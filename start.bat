@echo off
chcp 65001 > nul
title ZipUnlocker v3
echo ===============================
echo    ZipUnlocker v3 - Final Release
echo ===============================
echo.
pip install -r requirements.txt
python main.py