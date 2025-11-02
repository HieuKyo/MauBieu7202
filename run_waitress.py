"""
Waitress WSGI Server Runner for WordGen Django Application

This script starts the Waitress WSGI server for the Django application.
Waitress is a production-quality pure-Python WSGI server with cross-platform
support (Windows, Linux, macOS).

Usage:
    python run_waitress.py

Configuration:
    - Host: 0.0.0.0 (accessible from all network interfaces)
    - Port: 8000
    - Threads: 4 (can be adjusted based on your needs)
"""

import os
import sys

def main():
    # Set Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wordgen.settings')

    try:
        from waitress import serve
        from django.core.wsgi import get_wsgi_application
    except ImportError as e:
        print("Error: Required packages not installed.")
        print("Please run: pip install -r requirements.txt")
        print(f"Details: {e}")
        sys.exit(1)

    # Get the WSGI application
    application = get_wsgi_application()

    # Server configuration
    host = '0.0.0.0'  # Listen on all interfaces
    port = 8000        # Default port
    threads = 4        # Number of threads to handle requests

    print("=" * 60)
    print("Starting WordGen Django Application with Waitress")
    print("=" * 60)
    print(f"Host: {host}")
    print(f"Port: {port}")
    print(f"Threads: {threads}")
    print()
    print("Server URLs:")
    print(f"  - Local:   http://localhost:{port}")
    print(f"  - Network: http://0.0.0.0:{port}")
    print()
    print("Press CTRL+C to stop the server")
    print("=" * 60)
    print()

    try:
        # Start the server
        serve(
            application,
            host=host,
            port=port,
            threads=threads,
            channel_timeout=60,
            connection_limit=1000,
            cleanup_interval=30,
            url_scheme='http'
        )
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
