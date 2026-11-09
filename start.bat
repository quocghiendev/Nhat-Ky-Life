@echo off
chcp 65001 > nul
title Nhật Ký AI Thực Thời - NhatKyWeb

echo ========================================================
echo         KHỞI ĐỘNG NHẬT KÝ AI THỰC THỜI
echo ========================================================
echo.

cd /d "%~dp0"

IF NOT EXIST "venv\Scripts\python.exe" (
    echo [THÔNG BÁO] Chưa tìm thấy môi trường venv, đang khởi tạo...
    py -3.11 -m venv venv
    call venv\Scripts\pip.exe install -r requirements.txt
)

echo [INFO] Đang khởi động máy chủ Web...
venv\Scripts\python.exe run.py

pause
