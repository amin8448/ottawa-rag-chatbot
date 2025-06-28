#!/usr/bin/env python3
"""
Debug Ottawa RAG Pipeline components one by one
Find exactly what's failing
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_individual_imports():
    """Test each module import individually"""
    
    print("🔍 Testing Individual Module Imports")
    print("=" * 50)
    
    modules_to_test = [
        ('embeddings', 'EmbeddingManager'),
        ('vector_store', 'VectorStore'),
        ('llm_interface', 'LLMInterface'),
        ('data_processor', 'DataProcessor'),
        ('rag_pipeline', 'OttawaRAGPipeline'),
        ('chatbot', 'OttawaChatbot')
    ]
    
    results = {}
    
    for module_name, class_name in modules_to_test:
        try:
            print(f"📦 Testing {module_name}...")
            module = __import__(module_name)
            
            if hasattr(module, class_name):
                print(f"   ✅ {class_name} class found")
                
                # Try to instantiate with minimal config
                try:
                    if class_name == 'EmbeddingManager':
                        obj = getattr(module, class_name)()
                        print(f"   ✅ {class_name} can be instantiated")
                    elif class_name == 'VectorStore':
                        obj = getattr(module, class_name)()
                        print(f"   ✅ {class_name} can be instantiated")
                    elif class_name == 'LLMInterface':
                        obj = getattr(module, class_name)(api_key="test")
                        print(f"   ✅ {class_name} can be instantiated")
                    else:
                        print(f"   ⏸️  {class_name} - skipping instantiation test")
                    
                    results[module_name] = True
                    
                except Exception as e:
                    print(f"   ⚠️  {class_name} import OK but instantiation failed: {e}")
                    results[module_name] = "partial"
            else:
                print(f"   ❌ {class_name} class not found in module")
                results[module_name] = False
                
        except ImportError as e:
            print(f"   ❌ Import failed: {e}")
            results[module_name] = False
        except Exception as e:
            print(f"   ❌ Other error: {e}")
            results[module_name] = False
    
    return results

def test_data_availability():
    """Test if processed data is available"""
    
    print("\n📄 Testing Data Availability")
    print("=" * 30)
    
    data_file = Path("data/processed/ottawa_chunks.json")
    
    if data_file.exists():
        print("✅ Processed data file exists")
        
        try:
            import json
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            documents = data.get('documents', [])
            chunks = data.get('chunks', [])
            
            print(f"✅ Data loaded successfully")
            print(f"   📄 Documents: {len(documents)}")
            print(f"   📝 Chunks: {len(chunks)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    else:
        print(f"❌ Data file not found: {data_file}")
        print("   Run: python simple_processor.py")
        return False

def test_environment():
    """Test environment setup"""
    
    print("\n🔑 Testing Environment")
    print("=" * 25)
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ .env file exists")
        
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            
            api_key = os.getenv("GROQ_API_KEY")
            if api_key and len(api_key) > 10 and api_key != "your_groq_api_key_here":
                print("✅ Groq API key is set")
                return True
            else:
                print("⚠️  Groq API key not properly set")
                return False
                
        except Exception as e:
            print(f"❌ Error loading .env: {e}")
            return False
    else:
        print("❌ .env file not found")
        return False

def test_pipeline_creation():
    """Test creating the RAG pipeline"""
    
    print("\n🏗️ Testing Pipeline Creation")
    print("=" * 35)
    
    try:
        # Test basic imports first
        print("📦 Importing required modules...")
        from rag_pipeline import OttawaRAGPipeline
        print("✅ RAG pipeline import successful")
        
        # Test pipeline creation with minimal config
        print("🔧 Creating pipeline instance...")
        
        pipeline = OttawaRAGPipeline(
            data_path="data/processed/ottawa_chunks.json",
            groq_api_key=os.getenv("GROQ_API_KEY") or "dummy_key_for_testing"
        )
        
        print("✅ Pipeline instance created")
        
        # Test data loading
        print("📊 Testing data loading...")
        success = pipeline.load_full_dataset()
        
        if success:
            print("✅ Data loading successful")
            
            # Test vector database initialization
            print("🔍 Testing vector database...")
            try:
                db_success = pipeline.initialize_vector_database()
                if db_success:
                    print("✅ Vector database initialized")
                    return True
                else:
                    print("❌ Vector database initialization failed")
                    return False
            except Exception as e:
                print(f"❌ Vector database error: {e}")
                return False
        else:
            print("❌ Data loading failed")
            return False
            
    except Exception as e:
        print(f"❌ Pipeline creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main debugging function"""
    
    print("🔍 Ottawa RAG Pipeline Debugging")
    print("=" * 40)
    
    # Test 1: Individual imports
    import_results = test_individual_imports()
    
    # Test 2: Data availability
    data_ok = test_data_availability()
    
    # Test 3: Environment
    env_ok = test_environment()
    
    # Test 4: Pipeline creation (only if other tests pass)
    if all(import_results.values()) and data_ok and env_ok:
        pipeline_ok = test_pipeline_creation()
    else:
        print("\n⏸️  Skipping pipeline test - fix issues above first")
        pipeline_ok = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DEBUGGING SUMMARY")
    print("=" * 50)
    
    print("📦 Module Imports:")
    for module, status in import_results.items():
        if status is True:
            print(f"   ✅ {module}")
        elif status == "partial":
            print(f"   ⚠️  {module} (partial)")
        else:
            print(f"   ❌ {module}")
    
    print(f"📄 Data Available: {'✅' if data_ok else '❌'}")
    print(f"🔑 Environment: {'✅' if env_ok else '❌'}")
    print(f"🏗️ Pipeline: {'✅' if pipeline_ok else '❌'}")
    
    if all([all(import_results.values()), data_ok, env_ok, pipeline_ok]):
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 Your chatbot should work now!")
        print("   Run: python deployment/local/run_local.py")
        return 0
    else:
        print("\n⚠️  ISSUES FOUND - Fix the ❌ items above")
        
        # Provide specific next steps
        if not data_ok:
            print("\n🔧 Next step: Process your data")
            print("   Run: python simple_processor.py")
        
        if not env_ok:
            print("\n🔧 Next step: Set up your API key")
            print("   Run: echo GROQ_API_KEY=your_actual_key > .env")
        
        if not all(import_results.values()):
            print("\n🔧 Next step: Fix import issues")
            print("   Run: python simple_fix.py")
        
        return 1

if __name__ == "__main__":
    sys.exit(main())