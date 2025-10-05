#!/usr/bin/env python3
"""
Railway startup script for FileCraft
Handles PORT environment variable properly
"""
import os
import subprocess
import sys

def main():
    print("🚀 Starting FileCraft on Railway...")
    
    # Get port from environment or use default
    port = os.environ.get('PORT', '8000')
    print(f"Port: {port}")
    
    # Validate port is numeric
    try:
        port_int = int(port)
        if port_int < 1 or port_int > 65535:
            raise ValueError("Port out of range")
    except ValueError as e:
        print(f"❌ Invalid port '{port}': {e}")
        print("🔧 Using default port 8000")
        port = '8000'
    
    print(f"✅ Starting uvicorn on port {port}")
    
    # Start uvicorn
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'app.main:app',
        '--host', '0.0.0.0',
        '--port', port
    ]
    
    print(f"🌟 Command: {' '.join(cmd)}")
    os.execvp(sys.executable, cmd)

if __name__ == '__main__':
    main()