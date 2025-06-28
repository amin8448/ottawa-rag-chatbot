#!/usr/bin/env python3
"""
Simple data processor without LangChain dependencies
Uses basic text splitting instead of RecursiveCharacterTextSplitter
"""

import os
import json
import re
from typing import List, Dict, Any, Tuple
import logging
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse

class SimpleTextSplitter:
    """Simple text splitter without LangChain dependency"""
    
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap"""
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings within the last 100 characters
                search_start = max(end - 100, start)
                sentence_endings = ['.', '!', '?', '\n']
                
                best_break = -1
                for i in range(end - 1, search_start - 1, -1):
                    if text[i] in sentence_endings and i + 1 < len(text):
                        if text[i + 1] in [' ', '\n', '\t'] or i + 1 == len(text):
                            best_break = i + 1
                            break
                
                if best_break > 0:
                    end = best_break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            if start >= len(text) - self.chunk_overlap:
                break
        
        return chunks

class SimpleOttawaDataProcessor:
    """Simplified data processor without external dependencies"""
    
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
        
        # Create output directory
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize simple text splitter
        self.text_splitter = SimpleTextSplitter(chunk_size, chunk_overlap)
        
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
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def _validate_document(self, doc_data: Dict[str, Any]) -> bool:
        """Validate document has required fields and content"""
        if 'url' not in doc_data or 'content' not in doc_data:
            return False
        
        content = doc_data.get('content', "")
        if not isinstance(content, str) or len(content.strip()) < 50:
            return False
        
        return True
    
    def _generate_title_from_url(self, url: str) -> str:
        """Generate a readable title from the URL"""
        try:
            parsed = urlparse(url)
            path = parsed.path.strip('/')
            
            if not path:
                return "Ottawa Homepage"
            
            parts = path.split('/')
            
            if len(parts) >= 2:
                title_part = parts[-1] if parts[-1] else parts[-2]
            else:
                title_part = parts[0]
            
            title = title_part.replace('-', ' ').replace('_', ' ')
            title = ' '.join(word.capitalize() for word in title.split())
            
            if 'ottawa' not in title.lower():
                title = f"{title} - Ottawa"
            
            return title
            
        except Exception:
            return "Ottawa City Services"
    
    def load_raw_documents(self) -> List[Dict[str, Any]]:
        """Load documents from your JSON format"""
        try:
            documents = []
            
            if not self.raw_data_dir.exists():
                self.logger.warning(f"Raw data directory not found: {self.raw_data_dir}")
                return documents
            
            json_files = list(self.raw_data_dir.glob("*.json"))
            self.logger.info(f"Found {len(json_files)} raw document files")
            
            for json_file in json_files:
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        doc_data = json.load(f)
                    
                    if self._validate_document(doc_data):
                        url = doc_data['url']
                        content = doc_data['content']
                        timestamp = doc_data.get('timestamp', datetime.now().isoformat())
                        
                        title = self._generate_title_from_url(url)
                        
                        standardized_doc = {
                            'url': url,
                            'title': title,
                            'content': content,
                            'description': f"Ottawa city services information from {url}",
                            'scraped_at': timestamp,
                            'source_file': json_file.name,
                            'content_length': len(content)
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
        
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', ' ', text)
        text = re.sub(r'\.{2,}', '.', text)
        text = re.sub(r'\s+\.', '.', text)
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
                cleaned_content = self.clean_text(document['content'])
                
                if len(cleaned_content) < self.min_chunk_length:
                    self.logger.warning(f"Document too short, skipping: {document.get('url', 'unknown')}")
                    continue
                
                text_chunks = self.text_splitter.split_text(cleaned_content)
                
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
                            "keywords": [],  # Skip keywords for simplicity
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
        print("🏗️ Processing your Ottawa dataset (simple version)...")
        
        documents = self.load_raw_documents()
        if not documents:
            print("❌ No valid documents found")
            return [], []
        
        chunks = self.create_chunks(documents)
        if not chunks:
            print("❌ No chunks created")
            return documents, []
        
        success = self.save_processed_data(documents, chunks)
        if not success:
            print("❌ Failed to save processed data")
            return documents, chunks
        
        print(f"✅ Processed {len(documents)} documents into {len(chunks)} chunks")
        return documents, chunks

if __name__ == "__main__":
    processor = SimpleOttawaDataProcessor()
    documents, chunks = processor.process_full_dataset()