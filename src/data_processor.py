"""
Data Processor for Ottawa RAG Pipeline
Handles text processing, chunking, and dataset preparation
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
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Download required NLTK data
try:
    nltk.data.find("tokenizers/punkt")
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("punkt", quiet=True)
    nltk.download("stopwords", quiet=True)


class DataProcessor:
    """
    Processes raw scraped data into optimized chunks for RAG

    Features:
    - Intelligent text chunking with overlap
    - Content cleaning and normalization
    - Metadata preservation and enrichment
    - Quality filtering and validation
    - Multiple output formats (JSON, CSV, Parquet)
    """

    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 100,
        min_chunk_length: int = 50,
        raw_data_dir: str = "data/raw",
        processed_data_dir: str = "data/processed",
    ):
        """
        Initialize the data processor

        Args:
            chunk_size: Target size for text chunks (characters)
            chunk_overlap: Overlap between consecutive chunks
            min_chunk_length: Minimum acceptable chunk length
            raw_data_dir: Directory containing raw scraped data
            processed_data_dir: Directory for processed output
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_length = min_chunk_length
        self.raw_data_dir = Path(raw_data_dir)
        self.processed_data_dir = Path(processed_data_dir)

        # Create output directory
        self.processed_data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", ".", " ", ""],
        )

        # Initialize NLTK components
        self.stemmer = PorterStemmer()
        try:
            self.stop_words = set(stopwords.words("english"))
        except LookupError:
            self.stop_words = set()

        # Statistics tracking
        self.processing_stats = {
            "documents_processed": 0,
            "chunks_created": 0,
            "total_characters": 0,
            "avg_chunk_length": 0,
            "processing_errors": 0,
        }

        self._setup_logging()

    def _setup_logging(self):
        """Setup logging for data processing operations"""
        self.logger = logging.getLogger(__name__)

    def load_raw_documents(self) -> List[Dict[str, Any]]:
        """
        Load all raw documents from the scraped data directory

        Returns:
            List of document dictionaries with metadata
        """
        try:
            documents = []

            if not self.raw_data_dir.exists():
                self.logger.warning(
                    f"Raw data directory not found: {self.raw_data_dir}"
                )
                return documents

            # Find all JSON files in raw data directory
            json_files = list(self.raw_data_dir.glob("*.json"))

            self.logger.info(f"Found {len(json_files)} raw document files")

            for json_file in json_files:
                try:
                    with open(json_file, "r", encoding="utf-8") as f:
                        doc_data = json.load(f)

                    # Validate required fields
                    if self._validate_document(doc_data):
                        documents.append(doc_data)
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

    def _validate_document(self, doc_data: Dict[str, Any]) -> bool:
        """Validate that document has required fields"""
        required_fields = ["url", "content", "title"]
        return all(field in doc_data for field in required_fields)

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text content

        Args:
            text: Raw text content

        Returns:
            Cleaned text
        """
        try:
            if not text or not isinstance(text, str):
                return ""

            # Remove extra whitespace
            text = re.sub(r"\s+", " ", text)

            # Remove special characters but keep punctuation
            text = re.sub(r"[^\w\s\.\,\!\?\;\:\-\(\)]", " ", text)

            # Fix common formatting issues
            text = re.sub(r"\.{2,}", ".", text)  # Multiple periods
            text = re.sub(r"\s+\.", ".", text)  # Space before period
            text = re.sub(r"\.\s*\.", ".", text)  # Period space period

            # Remove URLs and email addresses (they're in metadata)
            text = re.sub(
                r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                "",
                text,
            )
            text = re.sub(r"\S+@\S+\.\S+", "", text)

            # Remove phone numbers (they're often in metadata)
            text = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "", text)

            # Clean up spacing
            text = re.sub(r"\s+", " ", text)
            text = text.strip()

            return text

        except Exception as e:
            self.logger.error(f"Error cleaning text: {e}")
            return text

    def extract_keywords(self, text: str, max_keywords: int = 20) -> List[str]:
        """
        Extract keywords from text using simple NLP

        Args:
            text: Text to analyze
            max_keywords: Maximum number of keywords to return

        Returns:
            List of extracted keywords
        """
        try:
            if not text:
                return []

            # Tokenize and convert to lowercase
            words = word_tokenize(text.lower())

            # Filter out stop words, punctuation, and short words
            keywords = [
                word
                for word in words
                if (word.isalpha() and len(word) > 2 and word not in self.stop_words)
            ]

            # Count word frequencies
            word_freq = {}
            for word in keywords:
                word_freq[word] = word_freq.get(word, 0) + 1

            # Sort by frequency and return top keywords
            sorted_keywords = sorted(
                word_freq.items(), key=lambda x: x[1], reverse=True
            )

            return [word for word, freq in sorted_keywords[:max_keywords]]

        except Exception as e:
            self.logger.error(f"Error extracting keywords: {e}")
            return []

    def create_chunks(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create optimized text chunks from documents

        Args:
            documents: List of document dictionaries

        Returns:
            List of chunk dictionaries with metadata
        """
        try:
            all_chunks = []
            chunk_id_counter = 0

            self.logger.info(f"Creating chunks from {len(documents)} documents")

            for doc_idx, document in enumerate(documents):
                try:
                    # Clean the content
                    cleaned_content = self.clean_text(document["content"])

                    if len(cleaned_content) < self.min_chunk_length:
                        self.logger.warning(
                            f"Document too short, skipping: {document.get('url', 'unknown')}"
                        )
                        continue

                    # Split into chunks
                    text_chunks = self.text_splitter.split_text(cleaned_content)

                    # Process each chunk
                    for chunk_idx, chunk_text in enumerate(text_chunks):
                        if len(chunk_text) >= self.min_chunk_length:

                            # Extract keywords for this chunk
                            keywords = self.extract_keywords(chunk_text)

                            # Create chunk dictionary
                            chunk = {
                                "id": f"chunk_{chunk_id_counter:06d}",
                                "document_id": f"doc_{doc_idx:06d}",
                                "chunk_index": chunk_idx,
                                "content": chunk_text,
                                "content_length": len(chunk_text),
                                "url": document.get("url", ""),
                                "title": document.get("title", ""),
                                "description": document.get("description", ""),
                                "source_file": document.get("source_file", ""),
                                "keywords": keywords,
                                "timestamp": document.get("scraped_at", ""),
                                "processed_at": datetime.now().isoformat(),
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
            self.processing_stats["total_characters"] = sum(
                chunk["content_length"] for chunk in all_chunks
            )

            if all_chunks:
                self.processing_stats["avg_chunk_length"] = self.processing_stats[
                    "total_characters"
                ] / len(all_chunks)

            self.logger.info(
                f"Created {len(all_chunks)} chunks from {len(documents)} documents"
            )

            return all_chunks

        except Exception as e:
            self.logger.error(f"Error creating chunks: {e}")
            return []

    def save_processed_data(
        self,
        documents: List[Dict[str, Any]],
        chunks: List[Dict[str, Any]],
        filename: str = "ottawa_chunks",
    ) -> bool:
        """
        Save processed data in multiple formats

        Args:
            documents: Original documents
            chunks: Processed chunks
            filename: Base filename for output files

        Returns:
            Success status
        """
        try:
            # Save as JSON (primary format for RAG pipeline)
            json_file = self.processed_data_dir / f"{filename}.json"
            json_data = {
                "metadata": {
                    "processing_date": datetime.now().isoformat(),
                    "chunk_size": self.chunk_size,
                    "chunk_overlap": self.chunk_overlap,
                    "min_chunk_length": self.min_chunk_length,
                    "statistics": self.processing_stats,
                },
                "documents": documents,
                "chunks": chunks,
            }

            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"Saved JSON data: {json_file}")

            # Save chunks as CSV for analysis
            if chunks:
                chunks_df = pd.DataFrame(chunks)
                csv_file = self.processed_data_dir / f"{filename}_chunks.csv"
                chunks_df.to_csv(csv_file, index=False, encoding="utf-8")

                self.logger.info(f"Saved CSV data: {csv_file}")

            # Save processing statistics
            stats_file = self.processed_data_dir / f"{filename}_stats.json"
            with open(stats_file, "w", encoding="utf-8") as f:
                json.dump(self.processing_stats, f, indent=2)

            self.logger.info(f"Saved statistics: {stats_file}")

            return True

        except Exception as e:
            self.logger.error(f"Error saving processed data: {e}")
            return False

    def validate_chunks(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate the quality of processed chunks

        Args:
            chunks: List of processed chunks

        Returns:
            Validation report
        """
        try:
            if not chunks:
                return {"status": "error", "message": "No chunks to validate"}

            # Calculate validation metrics
            chunk_lengths = [chunk["content_length"] for chunk in chunks]
            unique_sources = set(chunk["url"] for chunk in chunks)

            validation_report = {
                "total_chunks": len(chunks),
                "unique_sources": len(unique_sources),
                "avg_chunk_length": sum(chunk_lengths) / len(chunk_lengths),
                "min_chunk_length": min(chunk_lengths),
                "max_chunk_length": max(chunk_lengths),
                "chunks_below_min": sum(
                    1 for length in chunk_lengths if length < self.min_chunk_length
                ),
                "chunks_above_max": sum(
                    1 for length in chunk_lengths if length > self.chunk_size * 1.5
                ),
                "empty_chunks": sum(
                    1 for chunk in chunks if not chunk["content"].strip()
                ),
                "chunks_with_keywords": sum(
                    1 for chunk in chunks if chunk.get("keywords")
                ),
                "validation_passed": True,
            }

            # Check for issues
            issues = []
            if validation_report["chunks_below_min"] > 0:
                issues.append(
                    f"{validation_report['chunks_below_min']} chunks below minimum length"
                )

            if validation_report["empty_chunks"] > 0:
                issues.append(f"{validation_report['empty_chunks']} empty chunks found")

            if validation_report["chunks_with_keywords"] < len(chunks) * 0.8:
                issues.append("Less than 80% of chunks have keywords")

            validation_report["issues"] = issues
            validation_report["validation_passed"] = len(issues) == 0

            return validation_report

        except Exception as e:
            self.logger.error(f"Error validating chunks: {e}")
            return {"status": "error", "message": str(e)}

    def process_full_dataset(
        self, save_results: bool = True
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        Complete processing pipeline: load, clean, chunk, and save

        Args:
            save_results: Whether to save processed data to files

        Returns:
            Tuple of (documents, chunks)
        """
        try:
            self.logger.info("Starting full dataset processing")

            # Load raw documents
            documents = self.load_raw_documents()
            if not documents:
                self.logger.error("No documents loaded, cannot proceed")
                return [], []

            # Create chunks
            chunks = self.create_chunks(documents)
            if not chunks:
                self.logger.error("No chunks created, processing failed")
                return documents, []

            # Validate chunks
            validation_report = self.validate_chunks(chunks)
            self.logger.info(f"Validation report: {validation_report}")

            # Save results if requested
            if save_results:
                success = self.save_processed_data(documents, chunks)
                if success:
                    self.logger.info("Processing completed successfully")
                else:
                    self.logger.error("Error saving processed data")

            return documents, chunks

        except Exception as e:
            self.logger.error(f"Error in full dataset processing: {e}")
            return [], []

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics"""
        return {
            **self.processing_stats,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "min_chunk_length": self.min_chunk_length,
            "raw_data_dir": str(self.raw_data_dir),
            "processed_data_dir": str(self.processed_data_dir),
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize data processor
    processor = DataProcessor(
        chunk_size=800,
        chunk_overlap=100,
        min_chunk_length=50,
        raw_data_dir="data/raw",
        processed_data_dir="data/processed",
    )

    # Process full dataset
    documents, chunks = processor.process_full_dataset(save_results=True)

    print(f"Processed {len(documents)} documents into {len(chunks)} chunks")

    # Get processing statistics
    stats = processor.get_processing_stats()
    print(f"Processing stats: {stats}")

    # Validate chunks
    if chunks:
        validation = processor.validate_chunks(chunks)
        print(f"Validation report: {validation}")
