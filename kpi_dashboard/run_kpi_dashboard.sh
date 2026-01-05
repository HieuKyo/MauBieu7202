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

# Lấy IP LAN
LAN_IP=$(hostname -I | awk '{print $1}' 2>/dev/null)
if [ -z "$LAN_IP" ]; then
    # Fallback nếu hostname -I không hoạt động
    LAN_IP=$(ip addr show | grep 'inet ' | grep -v '127.0.0.1' | awk '{print $2}' | cut -d/ -f1 | head -n1)
fi

echo "📍 Địa chỉ truy cập:"
echo "   - Local:   http://localhost:8501"
if [ ! -z "$LAN_IP" ]; then
    echo "   - LAN:     http://$LAN_IP:8501"
    echo ""
    echo "💡 Các máy khác trong mạng LAN có thể truy cập qua:"
    echo "   http://$LAN_IP:8501"
fi
echo ""
echo "⚠️  Nhấn Ctrl+C để dừng ứng dụng"
echo ""
echo "=========================================="
echo ""

streamlit run app.py

