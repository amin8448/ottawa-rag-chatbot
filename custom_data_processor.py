"""
Custom data processor for your scraped Ottawa data format
Auto-generated based on your data structure
"""

import os
import json
import re
from typing import List, Dict, Any, Optional, Tuple
import logging
from pathlib import Path
from datetime import datetime

import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
import nltk

class CustomOttawaDataProcessor:
    """
    Custom data processor for your specific scraped data format
    """
    
    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        min_chunk_length: int = 50,
        raw_data_dir: str = "data/raw",
        processed_data_dir: str = "data/processed"
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_length = min_chunk_length
        self.raw_data_dir = Path(raw_data_dir)
        self.processed_data_dir = Path(processed_data_dir)
        
        # Field mapping for your data format
        self.field_mapping = {'url': 'url', 'content': 'content'}
        
        # Create output directory
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", ".", " ", ""]
        )
        
        # Statistics tracking
        self.processing_stats = {
            "documents_processed": 0,
            "chunks_created": 0,
            "total_characters": 0,
            "avg_chunk_length": 0,
            "processing_errors": 0
        }
        
        self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging"""
        self.logger = logging.getLogger(__name__)
        
    def _validate_document(self, doc_data: Dict[str, Any]) -> bool:
        """Validate document using your data format"""
        # Check if document has content field (most important)
        content_field = self.field_mapping.get('content')
        if not content_field or content_field not in doc_data:
            return False
        
        # Check if content is not empty
        content = doc_data.get(content_field, "")
        if not isinstance(content, str) or len(content.strip()) < 50:
            return False
        
        return True
    
    def _extract_field(self, doc_data: Dict[str, Any], field_name: str) -> str:
        """Extract field using field mapping"""
        actual_field = self.field_mapping.get(field_name, field_name)
        return str(doc_data.get(actual_field, "")).strip()
    
    def load_raw_documents(self) -> List[Dict[str, Any]]:
        """Load documents with your data format"""
        try:
            documents = []
            
            if not self.raw_data_dir.exists():
                self.logger.warning(f"Raw data directory not found: {self.raw_data_dir}")
                return documents
            
            # Find all JSON files
            json_files = list(self.raw_data_dir.glob("*.json"))
            self.logger.info(f"Found {len(json_files)} raw document files")
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        doc_data = json.load(f)
                    
                    # Validate and convert document
                    if self._validate_document(doc_data):
                        # Convert to standard format
                        standardized_doc = {
                            'url': self._extract_field(doc_data, 'url') or f"ottawa.ca/page/{json_file.stem}",
                            'title': self._extract_field(doc_data, 'title') or f"Ottawa Page {json_file.stem}",
                            'content': self._extract_field(doc_data, 'content'),
                            'description': self._extract_field(doc_data, 'description'),
                            'scraped_at': datetime.now().isoformat(),
                            'source_file': json_file.name,
                            'content_length': len(self._extract_field(doc_data, 'content'))
                        }
                        
                        documents.append(standardized_doc)
                    else:
                        self.logger.warning(f"Invalid document format: {json_file}")
                        
                except Exception as e:
                    self.logger.error(f"Error loading {json_file}: {e}")
                    self.processing_stats["processing_errors"] += 1
            
            self.logger.info(f"Successfully loaded {len(documents)} documents")
            return documents
            
        except Exception as e:
            self.logger.error(f"Error loading raw documents: {e}")
            return []
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text or not isinstance(text, str):
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
        
        # Fix common formatting issues
        text = re.sub(r'\.{2,}', '.', text)  # Multiple periods
        text = re.sub(r'\s+\.', '.', text)   # Space before period
        
        # Clean up spacing
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
    
    def create_chunks(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create text chunks from documents"""
        all_chunks = []
        chunk_id_counter = 0
        
        self.logger.info(f"Creating chunks from {len(documents)} documents")
        
        for doc_idx, document in enumerate(documents):
            try:
                # Clean the content
                cleaned_content = self.clean_text(document['content'])
                
                if len(cleaned_content) < self.min_chunk_length:
                    self.logger.warning(f"Document too short, skipping: {document.get('url', 'unknown')}")
                    continue
                
                # Split into chunks
                text_chunks = self.text_splitter.split_text(cleaned_content)
                
                # Process each chunk
                for chunk_idx, chunk_text in enumerate(text_chunks):
                    if len(chunk_text) >= self.min_chunk_length:
                        
                        chunk = {
                            "id": f"chunk_{chunk_id_counter:06d}",
                            "document_id": f"doc_{doc_idx:06d}",
                            "chunk_index": chunk_idx,
                            "content": chunk_text,
                            "content_length": len(chunk_text),
                            "url": document.get('url', ''),
                            "title": document.get('title', ''),
                            "description": document.get('description', ''),
                            "source_file": document.get('source_file', ''),
                            "keywords": [],  # Simple for now
                            "timestamp": document.get('scraped_at', ''),
                            "processed_at": datetime.now().isoformat()
                        }
                        
                        all_chunks.append(chunk)
                        chunk_id_counter += 1
                
                self.processing_stats["documents_processed"] += 1
                
            except Exception as e:
                self.logger.error(f"Error processing document {doc_idx}: {e}")
                self.processing_stats["processing_errors"] += 1
                continue
        
        # Update statistics
        self.processing_stats["chunks_created"] = len(all_chunks)
        self.processing_stats["total_characters"] = sum(chunk["content_length"] for chunk in all_chunks)
        
        if all_chunks:
            self.processing_stats["avg_chunk_length"] = (
                self.processing_stats["total_characters"] / len(all_chunks)
            )
        
        self.logger.info(f"Created {len(all_chunks)} chunks")
        return all_chunks
    
    def save_processed_data(self, documents: List[Dict[str, Any]], chunks: List[Dict[str, Any]]) -> bool:
        """Save processed data"""
        try:
            json_file = self.processed_data_dir / "ottawa_chunks.json"
            json_data = {
                "metadata": {
                    "processing_date": datetime.now().isoformat(),
                    "chunk_size": self.chunk_size,
                    "chunk_overlap": self.chunk_overlap,
                    "min_chunk_length": self.min_chunk_length,
                    "field_mapping": self.field_mapping,
                    "statistics": self.processing_stats
                },
                "documents": documents,
                "chunks": chunks
            }
            
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Saved processed data: {json_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving processed data: {e}")
            return False
    
    def process_full_dataset(self) -> Tuple[List[Dict], List[Dict]]:
        """Complete processing pipeline"""
        print("🏗️ Processing your Ottawa dataset...")
        
        # Load documents
        documents = self.load_raw_documents()
        if not documents:
            print("❌ No valid documents found")
            return [], []
        
        # Create chunks
        chunks = self.create_chunks(documents)
        if not chunks:
            print("❌ No chunks created")
            return documents, []
        
        # Save results
        success = self.save_processed_data(documents, chunks)
        if not success:
            print("❌ Failed to save processed data")
            return documents, chunks
        
        print(f"✅ Processed {len(documents)} documents into {len(chunks)} chunks")
        return documents, chunks

# Usage
if __name__ == "__main__":
    processor = CustomOttawaDataProcessor()
    documents, chunks = processor.process_full_dataset()
