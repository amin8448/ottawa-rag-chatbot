#!/usr/bin/env python3
"""
Quick test script to verify Ottawa RAG Chatbot setup
Run this before launching the full application
"""

import os
import sys
from pathlib import Path

def test_environment():
    """Test if environment is properly set up"""
    print("🧪 Testing Ottawa RAG Chatbot Setup")
    print("=" * 50)
    
    issues = []
    
    # Test 1: Python version
    print(f"✅ Python version: {sys.version}")
    
    # Test 2: Project structure
    project_root = Path(__file__).parent
    required_dirs = ['src', 'data', 'deployment']
    
    for dir_name in required_dirs:
        if (project_root / dir_name).exists():
            print(f"✅ Found directory: {dir_name}/")
        else:
            print(f"❌ Missing directory: {dir_name}/")
            issues.append(f"Missing {dir_name}/ directory")
    
    # Test 3: Source files
    src_files = [
        'scraper.py', 'data_processor.py', 'embeddings.py',
        'vector_store.py', 'llm_interface.py', 'rag_pipeline.py', 'chatbot.py'
    ]
    
    for file_name in src_files:
        if (project_root / 'src' / file_name).exists():
            print(f"✅ Found: src/{file_name}")
        else:
            print(f"❌ Missing: src/{file_name}")
            issues.append(f"Missing src/{file_name}")
    
    # Test 4: Environment file
    env_file = project_root / '.env'
    if env_file.exists():
        print("✅ Found: .env file")
        
        # Check if API key is set
        try:
            with open(env_file, 'r') as f:
                env_content = f.read()
            
            if 'GROQ_API_KEY=' in env_content and 'your_groq_api_key_here' not in env_content:
                print("✅ Groq API key appears to be set")
            else:
                print("⚠️  Groq API key not set or using placeholder")
                issues.append("API key not configured")
        except Exception as e:
            print(f"❌ Error reading .env file: {e}")
    else:
        print("❌ Missing: .env file")
        issues.append("Missing .env file")
    
    # Test 5: Package imports
    print("\n🔧 Testing Package Imports...")
    
    # Add src to path for imports
    sys.path.insert(0, str(project_root / 'src'))
    
    import_tests = [
        ('sentence_transformers', 'SentenceTransformers'),
        ('chromadb', 'ChromaDB'),
        ('gradio', 'Gradio'),
        ('groq', 'Groq API'),
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy')
    ]
    
    for module_name, display_name in import_tests:
        try:
            __import__(module_name)
            print(f"✅ {display_name}")
        except ImportError as e:
            print(f"❌ {display_name}: {e}")
            issues.append(f"Import error: {module_name}")
    
    # Test 6: Custom modules
    print("\n🏗️ Testing Custom Modules...")
    
    custom_modules = [
        ('embeddings', 'EmbeddingManager'),
        ('vector_store', 'VectorStore'),
        ('llm_interface', 'LLMInterface'),
        ('data_processor', 'DataProcessor'),
        ('rag_pipeline', 'OttawaRAGPipeline'),
        ('chatbot', 'OttawaChatbot')
    ]
    
    for module_name, class_name in custom_modules:
        try:
            module = __import__(module_name)
            if hasattr(module, class_name):
                print(f"✅ {class_name}")
            else:
                print(f"❌ {class_name}: Class not found")
                issues.append(f"Class not found: {class_name}")
        except ImportError as e:
            print(f"❌ {class_name}: {e}")
            issues.append(f"Import error: {module_name}")
    
    # Test 7: Data directory
    data_dir = project_root / 'data'
    if data_dir.exists():
        processed_data = data_dir / 'processed' / 'ottawa_chunks.json'
        if processed_data.exists():
            print("✅ Processed data found")
        else:
            print("⚠️  Processed data not found (will use demo data)")
            print(f"   Expected: {processed_data}")
    
    # Summary
    print("\n" + "=" * 50)
    if issues:
        print(f"⚠️  Found {len(issues)} issues:")
        for issue in issues:
            print(f"   • {issue}")
        print("\n💡 Fix these issues before running the chatbot")
        return False
    else:
        print("🎉 All tests passed! Ready to launch chatbot!")
        return True

def main():
    """Main test function"""
    success = test_environment()
    
    if success:
        print("\n🚀 Next steps:")
        print("1. Run: python deployment/local/run_local.py")
        print("2. Or run: python deployment/local/app.py")
        print("3. Open: http://localhost:7860")
        
        # Ask if they want to launch now
        try:
            choice = input("\n🤔 Would you like to launch the chatbot now? (y/n): ")
            if choice.lower().startswith('y'):
                print("\n🚀 Launching chatbot...")
                
                # Try to import and run the chatbot
                try:
                    from chatbot import OttawaChatbot
                    
                    # Quick configuration
                    config = {
                        "data_path": "data/processed/ottawa_chunks.json",
                        "groq_api_key": os.getenv("GROQ_API_KEY"),
                        "enable_admin": True,
                        "enable_analytics": True
                    }
                    
                    chatbot = OttawaChatbot(**config)
                    print("✅ Chatbot initialized successfully!")
                    print("🌐 Starting web interface at http://localhost:7860")
                    chatbot.launch()
                    
                except Exception as e:
                    print(f"❌ Error launching chatbot: {e}")
                    print("\n💡 Try running: python deployment/local/app.py")
                    
        except KeyboardInterrupt:
            print("\n👋 Test completed.")
    else:
        print("\n🔧 Please fix the issues above and run the test again.")
        return 1
    
    return 0

if __name__ == "__main__":
    # Load environment variables
    from pathlib import Path
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    exit_code = main()
    sys.exit(exit_code)