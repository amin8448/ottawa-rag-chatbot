#!/usr/bin/env python3
"""
Simple and direct fix for import issues
Directly replace problematic imports with working ones
"""

from pathlib import Path

def fix_rag_pipeline():
    """Fix rag_pipeline.py imports"""
    
    file_path = Path("src/rag_pipeline.py")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"🔧 Fixing {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and replace the import section
    new_lines = []
    in_import_section = False
    
    for line in lines:
        # Skip the problematic import section
        if "# Custom modules" in line and "use absolute imports for compatibility" in line:
            in_import_section = True
            # Replace with working imports
            new_lines.append("# Custom modules - absolute imports\n")
            new_lines.append("from embeddings import EmbeddingManager\n")
            new_lines.append("from vector_store import VectorStore\n")
            new_lines.append("from llm_interface import LLMInterface\n")
            continue
        
        if in_import_section and (line.startswith("from .") or line.startswith("except ImportError:") or "from embeddings import" in line or "from vector_store import" in line or "from llm_interface import" in line):
            # Skip these lines - we already added the correct imports
            continue
        
        if in_import_section and line.strip() == "":
            in_import_section = False
        
        if not in_import_section:
            new_lines.append(line)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ Fixed {file_path}")
    return True

def fix_chatbot():
    """Fix chatbot.py imports"""
    
    file_path = Path("src/chatbot.py")
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    print(f"🔧 Fixing {file_path}...")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and replace the import section
    new_lines = []
    in_import_section = False
    
    for line in lines:
        # Skip the problematic import section
        if "# Import your RAG pipeline components" in line and "use absolute imports for compatibility" in line:
            in_import_section = True
            # Replace with working imports
            new_lines.append("# Import your RAG pipeline components - absolute imports\n")
            new_lines.append("from rag_pipeline import OttawaRAGPipeline\n")
            new_lines.append("from data_processor import DataProcessor\n")
            new_lines.append("from embeddings import EmbeddingManager\n")
            new_lines.append("from vector_store import VectorStore\n")
            new_lines.append("from llm_interface import LLMInterface\n")
            continue
        
        if in_import_section and (line.startswith("try:") or line.startswith("from .") or line.startswith("except ImportError:") or "from rag_pipeline import" in line or "from data_processor import" in line):
            # Skip these lines - we already added the correct imports
            continue
        
        if in_import_section and line.strip() == "":
            in_import_section = False
        
        if not in_import_section:
            new_lines.append(line)
    
    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ Fixed {file_path}")
    return True

def main():
    """Main function"""
    
    print("🔧 Simple Import Fix for Ottawa RAG Chatbot")
    print("=" * 45)
    
    # Fix both files
    success1 = fix_rag_pipeline()
    success2 = fix_chatbot()
    
    if success1 and success2:
        print("\n✅ Import fixes completed!")
        print("\n🧪 Now test the fixes:")
        print("   python test_setup.py")
        print("\n🚀 If successful, launch the chatbot:")
        print("   python deployment/local/run_local.py")
        return 0
    else:
        print("\n❌ Some fixes failed")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())