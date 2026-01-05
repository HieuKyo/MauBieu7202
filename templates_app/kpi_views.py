"""
KPI Dashboard Views
===================
Views for the Bank KPI Dashboard feature
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
import subprocess
import socket
import os


def find_free_port(start_port=8501, max_port=8600):
    """
    Find a free port starting from start_port
    """
    for port in range(start_port, max_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    return None


@login_required
def kpi_dashboard_view(request):
    """
    View for KPI Dashboard landing page
    """
    context = {
        'page_title': 'Dashboard Tính KPI Ngân hàng',
        'streamlit_port': 8501,  # Default Streamlit port
    }
    return render(request, 'templates_app/kpi_dashboard.html', context)


@login_required
def kpi_dashboard_launch(request):
    """
    API endpoint to check if Streamlit is running or provide launch instructions
    """
    try:
        # Check if Streamlit is running on port 8501
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', 8501))

            if result == 0:
                return JsonResponse({
                    'status': 'running',
                    'url': 'http://localhost:8501',
                    'message': 'KPI Dashboard đang chạy'
                })
            else:
                return JsonResponse({
                    'status': 'stopped',
                    'message': 'KPI Dashboard chưa được khởi động',
                    'instructions': [
                        'Mở Terminal/Command Prompt',
                        'Di chuyển đến thư mục: cd kpi_dashboard',
                        'Chạy lệnh: streamlit run app.py',
                        'Hoặc chạy file: run_kpi_dashboard.bat (Windows) / run_kpi_dashboard.sh (Linux/Mac)'
                    ]
                })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Lỗi khi kiểm tra trạng thái: {str(e)}'
        })


@login_required
def kpi_dashboard_status(request):
    """
    Check if KPI Dashboard (Streamlit) is running
    """
    ports_to_check = [8501, 8502, 8503]  # Check common Streamlit ports

    for port in ports_to_check:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))

                if result == 0:
                    return JsonResponse({
                        'running': True,
                        'port': port,
                        'url': f'http://localhost:{port}'
                    })
        except:
            continue

    return JsonResponse({
        'running': False,
        'port': None,
        'url': None
    })
