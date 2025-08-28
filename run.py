#!/usr/bin/env python3
"""
CUNY Chatbot Startup Script
This script provides an easy way to start the chatbot with different configurations.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import flask
        import openai
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_openai_key():
    """Check if OpenAI API key is set"""
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key and api_key != 'your_openai_api_key_here':
        print("✅ OpenAI API key is configured")
        return True
    else:
        print("⚠️  OpenAI API key not found")
        print("   The chatbot will work with fallback responses only")
        print("   To enable full AI capabilities, set your OPENAI_API_KEY")
        return False

def run_tests():
    """Run the test suite"""
    print("\n🧪 Running tests...")
    try:
        result = subprocess.run([sys.executable, 'test_chatbot.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Tests passed!")
            return True
        else:
            print("❌ Tests failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def start_server():
    """Start the Flask server"""
    print("\n🚀 Starting CUNY Chatbot server...")
    print("   The chatbot will be available at: http://localhost:5000")
    print("   Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n👋 Server stopped. Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")

def main():
    """Main startup function"""
    print("🎓 CUNY AI Assistant - Enrollment Chatbot")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check OpenAI key
    has_openai = check_openai_key()
    
    # Run tests
    if not run_tests():
        print("\n❌ Tests failed. Please fix the issues before starting the server.")
        sys.exit(1)
    
    # Start server
    start_server()

if __name__ == "__main__":
    main()
