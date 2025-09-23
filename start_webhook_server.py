#!/usr/bin/env python3
"""
Startup script for AmoCRM-Manus webhook system
Optimized for GitHub Codespace deployment
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    try:
        import flask
        import sqlite3
        print("✅ All dependencies are available")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def setup_environment():
    """Setup environment variables and configuration"""
    
    # Set default configuration if not exists
    env_vars = {
        'FLASK_ENV': 'production',
        'FLASK_DEBUG': 'False',
        'PYTHONPATH': str(Path(__file__).parent)
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
    
    print("✅ Environment configured")

def get_codespace_url():
    """Get the Codespace URL for webhook configuration"""
    
    # Try to get Codespace URL from environment
    codespace_name = os.environ.get('CODESPACE_NAME')
    github_codespaces_port_forwarding_domain = os.environ.get('GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN')
    
    if codespace_name and github_codespaces_port_forwarding_domain:
        base_url = f"https://{codespace_name}-5000.{github_codespaces_port_forwarding_domain}"
        return base_url
    
    # Fallback to localhost for local development
    return "http://localhost:5000"

def print_webhook_urls():
    """Print webhook URLs for configuration"""
    
    base_url = get_codespace_url()
    
    print("\n" + "="*70)
    print("🚀 WEBHOOK SYSTEM STARTED")
    print("="*70)
    print(f"📍 Base URL: {base_url}")
    print(f"🔗 AmoCRM Webhook: {base_url}/amocrm-webhook")
    print(f"🔗 Manus Webhook: {base_url}/manus-webhook")
    print(f"📊 System Status: {base_url}/status")
    print(f"💚 Health Check: {base_url}/health")
    print("="*70)
    print("📋 CONFIGURATION STEPS:")
    print("1. Copy the webhook URLs above")
    print("2. Configure them in AmoCRM and Manus settings")
    print("3. Test the integration")
    print("="*70)

def start_webhook_server():
    """Start the webhook server"""
    
    print("🔄 Starting webhook server...")
    
    # Import and run the webhook system
    try:
        from complete_webhook_system import app
        
        # Print configuration info
        print_webhook_urls()
        
        # Start the Flask app
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True
        )
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

def main():
    """Main startup function"""
    
    print("🚀 AmoCRM-Manus Webhook System Startup")
    print("="*50)
    
    # Check dependencies
    if not check_dependencies():
        print("Installing dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Setup environment
    setup_environment()
    
    # Start server
    start_webhook_server()

if __name__ == "__main__":
    main()
