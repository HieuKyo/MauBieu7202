#!/bin/bash

# Script download packages cho offline deployment - Linux/Mac

echo "========================================"
echo "  KPI Dashboard - Offline Downloader"
echo "========================================"
echo ""

python3 download_offline_packages.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Download thất bại!"
    exit 1
fi

echo ""
echo "[SUCCESS] Hoàn thành!"
