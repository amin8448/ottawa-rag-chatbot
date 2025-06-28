#!/usr/bin/env python3
"""
Quick launch script for Ottawa RAG Chatbot
Usage: python deployment/local/run_local.py
"""

import os
import sys
from pathlib import Path

def main():
    """Quick launch with minimal setup"""
    
    print("🚀 Ottawa RAG Chatbot - Quick Launch")
    print("=" * 40)
    
    # Get project root
    current_dir = Path(__file__).parent
    project_root = current_dir.parent.parent
    
    # Change to project root directory
    os.chdir(project_root)
    
    # Check if .env exists
    env_file = project_root / ".env"
    if not env_file.exists():
        print("⚠️  .env file not found")
        print("   Creating basic .env file...")
        
        with open(env_file, 'w') as f:
            f.write("# Ottawa RAG Chatbot Environment Variables\n")
            f.write("GROQ_API_KEY=your_groq_api_key_here\n")
            f.write("# Add your actual Groq API key above\n")
        
        print("✅ Created .env file - please add your Groq API key")
    
    # Run the main app
    try:
        from deployment.local.app import main as app_main
        app_main()
    except ImportError:
        print("❌ Error importing app - running fallback mode")
        
        # Fallback: run app.py directly
        app_path = current_dir / "app.py"
        if app_path.exists():
            os.system(f"python {app_path}")
        else:
            print("❌ app.py not found")
            return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())