#!/usr/bin/env python3
"""
Process real scraped Ottawa data for RAG pipeline
Converts your 133 JSON files into processed chunks
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def process_ottawa_data():
    """Process the real Ottawa scraped data"""
    
    print("🏛️ Processing Real Ottawa Data")
    print("=" * 50)
    
    # Check if raw data exists
    project_root = Path(__file__).parent
    raw_data_dir = project_root / "data" / "raw"
    
    if not raw_data_dir.exists():
        print(f"❌ Raw data directory not found: {raw_data_dir}")
        print("Please copy your JSON files to data/raw/ first")
        return False
    
    # Count JSON files
    json_files = list(raw_data_dir.glob("*.json"))
    print(f"📄 Found {len(json_files)} JSON files in {raw_data_dir}")
    
    if len(json_files) == 0:
        print("❌ No JSON files found in data/raw/")
        print("Please copy your scraped JSON files to data/raw/ first")
        return False
    
    # Show sample file names
    print("📋 Sample files:")
    for i, file_path in enumerate(sorted(json_files)[:5]):
        print(f"   • {file_path.name}")
    if len(json_files) > 5:
        print(f"   ... and {len(json_files) - 5} more files")
    
    try:
        # Import the data processor
        print("\n🔧 Importing data processor...")
        from data_processor import DataProcessor
        
        # Initialize data processor with your settings
        processor = DataProcessor(
            chunk_size=800,           # 800 characters per chunk
            chunk_overlap=100,        # 100 character overlap
            min_chunk_length=50,      # Minimum 50 characters
            raw_data_dir=str(raw_data_dir),
            processed_data_dir=str(project_root / "data" / "processed")
        )
        
        print("✅ Data processor initialized")
        
        # Process the full dataset
        print("\n📊 Processing your Ottawa dataset...")
        print("This may take a few minutes for 133 documents...")
        
        documents, chunks = processor.process_full_dataset(save_results=True)
        
        if not documents:
            print("❌ No documents were processed")
            return False
        
        if not chunks:
            print("❌ No chunks were created")
            return False
        
        # Show processing results
        print("\n" + "=" * 50)
        print("🎉 Processing completed successfully!")
        print(f"📄 Documents processed: {len(documents)}")
        print(f"📝 Text chunks created: {len(chunks)}")
        
        # Get processing statistics
        stats = processor.get_processing_stats()
        print(f"📊 Total characters: {stats['total_characters']:,}")
        print(f"📏 Average chunk length: {stats['avg_chunk_length']:.0f}")
        
        # Validate the chunks
        print("\n🔍 Validating processed data...")
        validation_report = processor.validate_chunks(chunks)
        
        if validation_report.get('validation_passed', False):
            print("✅ Data validation passed!")
        else:
            print("⚠️  Data validation found issues:")
            for issue in validation_report.get('issues', []):
                print(f"   • {issue}")
        
        # Check output file
        output_file = project_root / "data" / "processed" / "ottawa_chunks.json"
        if output_file.exists():
            file_size = output_file.stat().st_size / (1024 * 1024)  # MB
            print(f"💾 Output file: {output_file}")
            print(f"📦 File size: {file_size:.1f} MB")
        
        print("\n🚀 Your real Ottawa data is ready for the RAG pipeline!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you've created the __init__.py file in src/:")
        print("   echo. > src\\__init__.py")
        return False
    except Exception as e:
        print(f"❌ Processing error: {e}")
        return False

def check_data_format():
    """Check the format of your scraped data"""
    
    print("\n🔍 Checking your data format...")
    
    raw_data_dir = Path(__file__).parent / "data" / "raw"
    json_files = list(raw_data_dir.glob("*.json"))
    
    if not json_files:
        print("❌ No JSON files found")
        return False
    
    # Check first file to understand format
    import json
    
    sample_file = json_files[0]
    print(f"📄 Examining sample file: {sample_file.name}")
    
    try:
        with open(sample_file, 'r', encoding='utf-8') as f:
            sample_data = json.load(f)
        
        print("✅ Valid JSON format")
        print("🔍 Data structure:")
        
        if isinstance(sample_data, dict):
            for key in sample_data.keys():
                value = sample_data[key]
                if isinstance(value, str):
                    preview = value[:100] + "..." if len(value) > 100 else value
                    print(f"   • {key}: {preview}")
                else:
                    print(f"   • {key}: {type(value).__name__}")
        else:
            print(f"   Data type: {type(sample_data).__name__}")
        
        # Check if it has expected fields
        expected_fields = ['url', 'content', 'title']
        missing_fields = [field for field in expected_fields if field not in sample_data]
        
        if missing_fields:
            print(f"⚠️  Missing expected fields: {missing_fields}")
            print("   The data processor might need adjustment")
        else:
            print("✅ Data format looks compatible!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading sample file: {e}")
        return False

def main():
    """Main processing function"""
    
    # First check data format
    if not check_data_format():
        print("\n❌ Please check your data format and try again")
        return 1
    
    # Process the data
    success = process_ottawa_data()
    
    if success:
        print("\n🎯 Next steps:")
        print("1. Run: python test_setup.py")
        print("2. Run: python deployment/local/run_local.py")
        print("3. Open: http://localhost:7860")
        print("\n🌟 Your chatbot will now use real Ottawa data!")
        return 0
    else:
        print("\n❌ Processing failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())