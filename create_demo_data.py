#!/usr/bin/env python3
"""
Create demo data for Ottawa RAG Chatbot
Run this to generate sample data for testing
"""

import json
from pathlib import Path
from datetime import datetime

def create_demo_data():
    """Create demo Ottawa city services data"""
    
    print("🏗️ Creating demo data for Ottawa RAG Chatbot...")
    
    # Create data directories
    project_root = Path(__file__).parent
    data_dir = project_root / "data"
    processed_dir = data_dir / "processed"
    raw_dir = data_dir / "raw"
    embeddings_dir = data_dir / "embeddings"
    
    # Create directories
    for directory in [processed_dir, raw_dir, embeddings_dir]:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Demo Ottawa city services data
    demo_documents = [
        {
            "url": "https://ottawa.ca/en/residents/marriage-licenses",
            "title": "Marriage Licenses - City of Ottawa",
            "description": "Information about applying for marriage licenses in Ottawa",
            "content": "To apply for a marriage license in Ottawa, both parties must appear in person at City Hall located at 110 Laurier Avenue West. You need to bring valid government-issued photo identification and birth certificate or equivalent document. The fee is $145 and can be paid by cash, debit, or credit card. The license is valid for 90 days from the date of issue. Office hours are Monday to Friday, 8:30 AM to 4:30 PM.",
            "content_length": 456,
            "scraped_at": datetime.now().isoformat(),
            "source_file": "marriage_licenses.json"
        },
        {
            "url": "https://ottawa.ca/en/parking-transit-and-streets/parking",
            "title": "Parking Information - City of Ottawa", 
            "description": "Parking regulations and information for Ottawa",
            "content": "Parking in downtown Ottawa is managed through various methods. You can use the ParkByPhone app or pay at parking meters. Parking rates vary by zone and time of day. Monday to Saturday, parking enforcement operates from 7:00 AM to 6:00 PM. Sunday is generally free parking on most streets, except during special events. Parking violations can result in fines ranging from $30 to $100.",
            "content_length": 420,
            "scraped_at": datetime.now().isoformat(),
            "source_file": "parking_info.json"
        },
        {
            "url": "https://ottawa.ca/en/garbage-and-recycling",
            "title": "Garbage and Recycling - City of Ottawa",
            "description": "Waste collection and recycling information",
            "content": "Ottawa provides weekly garbage collection and bi-weekly recycling collection. Green bins are collected weekly for organic waste including food scraps, yard waste, and compostable materials. Blue and black bins are for recyclables and garbage respectively. Collection typically occurs early morning, so bins should be placed at the curb by 7:00 AM on collection day. Bulk item pickup is available by appointment.",
            "content_length": 445,
            "scraped_at": datetime.now().isoformat(),
            "source_file": "waste_collection.json"
        },
        {
            "url": "https://ottawa.ca/en/planning-development-and-construction/building-and-renovating/building-permits",
            "title": "Building Permits - City of Ottawa",
            "description": "Information about building permits and applications",
            "content": "Building permits are required for most construction projects in Ottawa including new construction, additions, renovations, and some repairs. Applications can be submitted online through the city portal or in person at City Hall. Processing times vary depending on the complexity of the project. Simple permits may be processed within 5-10 business days, while complex projects may take several weeks. Fees are based on the construction value.",
            "content_length": 485,
            "scraped_at": datetime.now().isoformat(),
            "source_file": "building_permits.json"
        },
        {
            "url": "https://ottawa.ca/en/health-and-public-safety/emergency-services",
            "title": "Emergency Services - City of Ottawa",
            "description": "Emergency services and fire safety information",
            "content": "Ottawa Fire Services provides fire protection, emergency medical services, and technical rescue services. For emergencies, call 911. For non-emergency fire safety questions, contact the Fire Prevention Office. Backyard fire permits are required for outdoor burning and can be obtained online. Fire bans may be in effect during dry conditions. Smoke alarms must be installed on every level of your home and tested monthly.",
            "content_length": 475,
            "scraped_at": datetime.now().isoformat(),
            "source_file": "emergency_services.json"
        }
    ]
    
    # Create text chunks from documents
    demo_chunks = []
    chunk_id = 1
    
    for doc_idx, document in enumerate(demo_documents):
        # Split content into chunks (simulate the chunking process)
        content = document["content"]
        
        # Simple chunking - split into ~200 character chunks with overlap
        chunk_size = 200
        overlap = 50
        
        start = 0
        chunk_index = 0
        
        while start < len(content):
            end = min(start + chunk_size, len(content))
            chunk_text = content[start:end]
            
            # Don't create tiny chunks
            if len(chunk_text) >= 50:
                chunk = {
                    "id": f"chunk_{chunk_id:06d}",
                    "document_id": f"doc_{doc_idx + 1:06d}",
                    "chunk_index": chunk_index,
                    "content": chunk_text,
                    "content_length": len(chunk_text),
                    "url": document["url"],
                    "title": document["title"],
                    "description": document["description"],
                    "source_file": document["source_file"],
                    "keywords": extract_keywords(chunk_text),
                    "timestamp": document["scraped_at"],
                    "processed_at": datetime.now().isoformat()
                }
                
                demo_chunks.append(chunk)
                chunk_id += 1
                chunk_index += 1
            
            # Move start position with overlap
            start += chunk_size - overlap
            if start >= len(content) - overlap:
                break
    
    # Create the processed data structure
    processed_data = {
        "metadata": {
            "processing_date": datetime.now().isoformat(),
            "chunk_size": 200,
            "chunk_overlap": 50,
            "min_chunk_length": 50,
            "statistics": {
                "documents_processed": len(demo_documents),
                "chunks_created": len(demo_chunks),
                "total_characters": sum(len(chunk["content"]) for chunk in demo_chunks),
                "avg_chunk_length": sum(len(chunk["content"]) for chunk in demo_chunks) / len(demo_chunks),
                "processing_errors": 0
            }
        },
        "documents": demo_documents,
        "chunks": demo_chunks
    }
    
    # Save processed data
    processed_file = processed_dir / "ottawa_chunks.json"
    with open(processed_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Created processed data: {processed_file}")
    print(f"📊 Generated {len(demo_documents)} documents and {len(demo_chunks)} chunks")
    
    # Also save individual raw documents for completeness
    for document in demo_documents:
        raw_file = raw_dir / document["source_file"]
        with open(raw_file, 'w', encoding='utf-8') as f:
            json.dump(document, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Created {len(demo_documents)} raw document files")
    
    return processed_file

def extract_keywords(text):
    """Simple keyword extraction"""
    # Simple approach: common Ottawa service words
    ottawa_keywords = [
        "ottawa", "city", "hall", "permit", "license", "application", 
        "fee", "parking", "garbage", "recycling", "fire", "emergency",
        "building", "marriage", "collection", "downtown", "services"
    ]
    
    text_lower = text.lower()
    found_keywords = [kw for kw in ottawa_keywords if kw in text_lower]
    
    # Add some general keywords
    words = text_lower.split()
    important_words = [w for w in words if len(w) > 4 and w.isalpha()]
    
    all_keywords = list(set(found_keywords + important_words[:5]))
    return all_keywords[:10]  # Limit to 10 keywords

def main():
    """Main function"""
    try:
        processed_file = create_demo_data()
        
        print("\n🎉 Demo data creation completed successfully!")
        print(f"📄 Data file: {processed_file}")
        print("\n🚀 You can now run the chatbot:")
        print("   python deployment/local/run_local.py")
        print("   python test_setup.py")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error creating demo data: {e}")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())