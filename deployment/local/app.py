"""
Local Deployment for Ottawa RAG Chatbot
Enhanced version with configuration management and error handling
"""

import os
import sys
from pathlib import Path
import logging
from dotenv import load_dotenv

# Add src to path for imports
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Load environment variables
load_dotenv(project_root / ".env")

# Import chatbot
try:
    from chatbot import OttawaChatbot
except ImportError as e:
    print(f"❌ Error importing chatbot: {e}")
    print("Make sure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)

def setup_logging():
    """Setup logging for local deployment"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('ottawa_chatbot.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_environment():
    """Check if environment is properly configured"""
    issues = []
    
    # Check API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        issues.append("❌ GROQ_API_KEY not found in environment variables")
    else:
        print("✅ Groq API key found")
    
    # Check data directory
    data_path = project_root / "data" / "processed" / "ottawa_chunks.json"
    if not data_path.exists():
        issues.append(f"❌ Data file not found: {data_path}")
        print(f"   Run: python scripts/process_data.py to create processed data")
    else:
        print("✅ Processed data found")
    
    # Check source code
    required_modules = [
        "scraper.py", "data_processor.py", "embeddings.py", 
        "vector_store.py", "llm_interface.py", "rag_pipeline.py", "chatbot.py"
    ]
    
    for module in required_modules:
        if not (src_path / module).exists():
            issues.append(f"❌ Missing module: src/{module}")
        else:
            print(f"✅ Found: src/{module}")
    
    return issues

def main():
    """Main function for local deployment"""
    
    print("🏛️ Ottawa City Services RAG Chatbot - Local Deployment")
    print("=" * 60)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Check environment
    print("\n🔍 Checking Environment...")
    issues = check_environment()
    
    if issues:
        print(f"\n⚠️  Found {len(issues)} issue(s):")
        for issue in issues:
            print(f"   {issue}")
        print("\n💡 The chatbot will run in demo mode with limited functionality")
        print("   Fix the issues above for full functionality")
    else:
        print("\n✅ Environment check passed - all systems ready!")
    
    # Configuration
    config = {
        "data_path": str(project_root / "data" / "processed" / "ottawa_chunks.json"),
        "groq_api_key": os.getenv("GROQ_API_KEY"),
        "enable_admin": True,
        "enable_analytics": True
    }
    
    print(f"\n🚀 Launching chatbot...")
    print(f"   Data path: {config['data_path']}")
    print(f"   Admin panel: {'Enabled' if config['enable_admin'] else 'Disabled'}")
    print(f"   Analytics: {'Enabled' if config['enable_analytics'] else 'Disabled'}")
    print(f"   LLM: {'Configured' if config['groq_api_key'] else 'Demo mode'}")
    
    try:
        # Initialize chatbot
        chatbot = OttawaChatbot(**config)
        
        # Launch interface
        print(f"\n🌐 Starting web interface...")
        print(f"   URL: http://localhost:7860")
        print(f"   Press Ctrl+C to stop the server")
        
        chatbot.launch(
            share=False,
            server_name="127.0.0.1",
            server_port=7860,
            debug=False
        )
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down chatbot...")
        logger.info("Chatbot shutdown by user")
    except Exception as e:
        print(f"\n❌ Error launching chatbot: {e}")
        logger.error(f"Chatbot launch error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)