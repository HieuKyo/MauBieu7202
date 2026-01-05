#!/bin/bash

# Script chạy KPI Dashboard trên Linux/Mac

echo "========================================"
echo "   KPI Dashboard - Agribank"
echo "========================================"
echo ""

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python chưa được cài đặt!"
    echo "Vui lòng cài đặt Python từ https://www.python.org/"
    exit 1
fi

# Kiểm tra Streamlit
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "[INFO] Đang cài đặt Streamlit..."
    pip3 install streamlit
fi

echo "[INFO] Khởi động ứng dụng..."
echo ""
echo "Ứng dụng sẽ mở tại: http://localhost:8501"
echo "Nhấn Ctrl+C để dừng ứng dụng"
echo ""

streamlit run app.py
