#!/usr/bin/env python3
"""
Direct chatbot launch script
Bypasses deployment complexity and runs the chatbot directly
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def main():
    """Launch the Ottawa RAG Chatbot directly"""
    
    print("🏛️ Ottawa City Services RAG Chatbot")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv(".env")
    
    # Check API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("⚠️  Warning: GROQ_API_KEY not found - running in demo mode")
    else:
        print("✅ Groq API key found")
    
    # Check data
    data_path = Path("data/processed/ottawa_chunks.json")
    if not data_path.exists():
        print("❌ Processed data not found. Run: python simple_processor.py")
        return 1
    else:
        print("✅ Processed data found")
    
    try:
        print("\n🚀 Importing chatbot...")
        from chatbot import OttawaChatbot
        
        print("✅ Chatbot imported successfully")
        
        # Configure chatbot
        config = {
            "data_path": str(data_path),
            "groq_api_key": api_key,
            "enable_admin": True,
            "enable_analytics": True
        }
        
        print("🔧 Initializing chatbot...")
        chatbot = OttawaChatbot(**config)
        
        print("✅ Chatbot initialized successfully!")
        print("\n🌐 Starting web interface...")
        print("   URL: http://localhost:7860")
        print("   Press Ctrl+C to stop")
        print("\n" + "=" * 50)
        
        # Launch chatbot
        chatbot.launch(
            share=False,
            server_name="127.0.0.1",
            server_port=7860,
            debug=False
        )
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down chatbot...")
        return 0
    except Exception as e:
        print(f"\n❌ Error launching chatbot: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure all tests passed: python debug_pipeline.py")
        print("2. Check your .env file has GROQ_API_KEY")
        print("3. Make sure processed data exists: python simple_processor.py")
        
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())