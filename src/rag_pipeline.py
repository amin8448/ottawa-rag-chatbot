"""
Complete RAG Pipeline for Ottawa City Services
Based on your Databricks implementation with full dataset
"""

import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

# Core ML libraries
from sentence_transformers import SentenceTransformer
import chromadb
from groq import Groq

# Data processing
import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Custom modules
from .embeddings import EmbeddingManager
from .vector_store import VectorStore
from .llm_interface import LLMInterface

class OttawaRAGPipeline:
    """
    Complete RAG Pipeline for Ottawa City Services
    
    This implementation uses:
    - 133 scraped Ottawa documents
    - 1,410 text chunks with overlap
    - SentenceTransformers embeddings (384-dim)
    - ChromaDB for vector storage
    - Groq API for LLM generation
    """
    
    def __init__(
        self,
        data_path: str = "data/processed/ottawa_chunks.json",
        embedding_model: str = "all-MiniLM-L6-v2",
        groq_api_key: Optional[str] = None,
        vector_db_path: str = "data/embeddings/chroma_db"
    ):
        """Initialize the complete RAG pipeline"""
        
        self.data_path = Path(data_path)
        self.vector_db_path = Path(vector_db_path)
        
        # Initialize components
        self.embedding_manager = EmbeddingManager(model_name=embedding_model)
        self.vector_store = VectorStore(db_path=str(self.vector_db_path))
        self.llm_interface = LLMInterface(api_key=groq_api_key)
        
        # Data storage
        self.documents = []
        self.chunks = []
        self.is_initialized = False
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure logging for the pipeline"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def load_full_dataset(self) -> bool:
        """
        Load the complete Ottawa dataset (133 documents, 1,410 chunks)
        This is your full Databricks dataset
        """
        try:
            self.logger.info("Loading complete Ottawa dataset...")
            
            # Load processed chunks
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.documents = data.get('documents', [])
            self.chunks = data.get('chunks', [])
            
            self.logger.info(f"Loaded {len(self.documents)} documents")
            self.logger.info(f"Loaded {len(self.chunks)} text chunks")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading dataset: {e}")
            return False
    
    def initialize_vector_database(self) -> bool:
        """
        Initialize ChromaDB with complete dataset
        Creates embeddings for all 1,410 chunks
        """
        try:
            self.logger.info("Initializing vector database...")
            
            if not self.chunks:
                self.logger.error("No chunks loaded. Call load_full_dataset() first.")
                return False
            
            # Generate embeddings for all chunks
            chunk_texts = [chunk['content'] for chunk in self.chunks]
            embeddings = self.embedding_manager.generate_embeddings(chunk_texts)
            
            # Setup vector store
            self.vector_store.create_collection("ottawa_complete")
            
            # Add all chunks to vector store
            chunk_ids = [chunk['id'] for chunk in self.chunks]
            metadatas = [{
                'url': chunk['url'],
                'source_file': chunk['source_file'],
                'chunk_index': chunk['chunk_index']
            } for chunk in self.chunks]
            
            self.vector_store.add_documents(
                ids=chunk_ids,
                documents=chunk_texts,
                embeddings=embeddings,
                metadatas=metadatas
            )
            
            self.is_initialized = True
            self.logger.info("Vector database initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing vector database: {e}")
            return False
    
    def search_relevant_context(
        self, 
        query: str, 
        top_k: int = 5,
        similarity_threshold: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant context using semantic similarity
        
        Args:
            query: User question
            top_k: Number of chunks to retrieve
            similarity_threshold: Minimum similarity score
            
        Returns:
            List of relevant chunks with metadata
        """
        try:
            if not self.is_initialized:
                self.logger.error("Pipeline not initialized. Call initialize_vector_database() first.")
                return []
            
            # Generate query embedding
            query_embedding = self.embedding_manager.generate_embeddings([query])[0]
            
            # Search vector store
            results = self.vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k
            )
            
            # Filter by similarity threshold
            relevant_chunks = []
            for result in results:
                if result.get('similarity', 0) >= similarity_threshold:
                    relevant_chunks.append(result)
            
            self.logger.info(f"Found {len(relevant_chunks)} relevant chunks for query")
            return relevant_chunks
            
        except Exception as e:
            self.logger.error(f"Error searching context: {e}")
            return []
    
    def generate_response(
        self, 
        query: str, 
        context_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate natural language response using retrieved context
        
        Args:
            query: User question
            context_chunks: Retrieved relevant chunks
            
        Returns:
            Response with answer, sources, and metadata
        """
        try:
            if not context_chunks:
                return {
                    "answer": "I couldn't find relevant information about that topic in my Ottawa database.",
                    "sources": [],
                    "confidence": 0.0
                }
            
            # Format context
            context_text = "\n\n".join([
                f"Source {i+1}: {chunk['document']}" 
                for i, chunk in enumerate(context_chunks)
            ])
            
            # Generate response using LLM
            response = self.llm_interface.generate_response(
                query=query,
                context=context_text
            )
            
            # Extract sources
            sources = []
            for chunk in context_chunks:
                metadata = chunk.get('metadata', {})
                sources.append({
                    'url': metadata.get('url', ''),
                    'source_file': metadata.get('source_file', ''),
                    'similarity': chunk.get('similarity', 0.0)
                })
            
            return {
                "answer": response,
                "sources": sources,
                "confidence": np.mean([chunk.get('similarity', 0) for chunk in context_chunks]),
                "chunks_used": len(context_chunks)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            return {
                "answer": f"I encountered an error processing your question: {str(e)}",
                "sources": [],
                "confidence": 0.0
            }
    
    def answer_question(self, question: str) -> Dict[str, Any]:
        """
        Complete RAG pipeline: retrieve relevant context and generate answer
        
        Args:
            question: User's question about Ottawa services
            
        Returns:
            Complete response with answer, sources, and metadata
        """
        try:
            self.logger.info(f"Processing question: {question}")
            
            # Step 1: Retrieve relevant context
            relevant_chunks = self.search_relevant_context(question, top_k=5)
            
            # Step 2: Generate response
            response = self.generate_response(question, relevant_chunks)
            
            # Step 3: Add pipeline metadata
            response.update({
                "query": question,
                "timestamp": pd.Timestamp.now().isoformat(),
                "pipeline_version": "1.0.0",
                "total_documents": len(self.documents),
                "total_chunks": len(self.chunks)
            })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error in RAG pipeline: {e}")
            return {
                "answer": "I encountered an unexpected error. Please try rephrasing your question.",
                "sources": [],
                "confidence": 0.0,
                "error": str(e)
            }
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            "documents_loaded": len(self.documents),
            "chunks_available": len(self.chunks),
            "embedding_model": self.embedding_manager.model_name,
            "embedding_dimension": self.embedding_manager.embedding_dimension,
            "vector_db_initialized": self.is_initialized,
            "llm_available": self.llm_interface.is_available(),
            "data_source": str(self.data_path),
            "vector_db_path": str(self.vector_db_path)
        }

# Example usage
if __name__ == "__main__":
    # Initialize pipeline with full dataset
    pipeline = OttawaRAGPipeline(
        data_path="data/processed/ottawa_chunks.json",
        groq_api_key=os.getenv("GROQ_API_KEY")
    )
    
    # Load complete dataset
    pipeline.load_full_dataset()
    
    # Initialize vector database
    pipeline.initialize_vector_database()
    
    # Test the system
    test_questions = [
        "How do I apply for a marriage license?",
        "What are the rules for backyard fires?",
        "What can I put in my green bin?"
    ]
    
    for question in test_questions:
        response = pipeline.answer_question(question)
        print(f"Q: {question}")
        print(f"A: {response['answer']}")
        print(f"Sources: {len(response['sources'])}")
        print(f"Confidence: {response['confidence']:.2f}")
        print("-" * 50)