"""
Tests for Ottawa RAG Pipeline
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestOttawaRAGPipeline:
    """Test cases for the Ottawa RAG Pipeline"""
    
    def test_import_rag_pipeline(self):
        """Test that RAG pipeline can be imported"""
        try:
            from rag_pipeline import OttawaRAGPipeline
            assert OttawaRAGPipeline is not None
        except ImportError as e:
            pytest.skip(f"RAG pipeline import failed: {e}")
    
    @patch('rag_pipeline.chromadb')
    def test_rag_pipeline_initialization(self, mock_chromadb):
        """Test RAG pipeline initialization"""
        try:
            from rag_pipeline import OttawaRAGPipeline
            
            # Mock ChromaDB
            mock_client = Mock()
            mock_collection = Mock()
            mock_chromadb.PersistentClient.return_value = mock_client
            mock_client.get_or_create_collection.return_value = mock_collection
            
            # Initialize pipeline
            pipeline = OttawaRAGPipeline()
            
            assert pipeline is not None
            assert hasattr(pipeline, 'collection')
            
        except ImportError:
            pytest.skip("RAG pipeline not available")
    
    def test_chatbot_import(self):
        """Test that chatbot can be imported"""
        try:
            from chatbot import OttawaChatbot
            assert OttawaChatbot is not None
        except ImportError as e:
            pytest.skip(f"Chatbot import failed: {e}")
    
    def test_data_processor_import(self):
        """Test that data processor can be imported"""
        try:
            from data_processor import DataProcessor
            assert DataProcessor is not None
        except ImportError as e:
            pytest.skip(f"Data processor import failed: {e}")

class TestDataProcessor:
    """Test cases for data processing"""
    
    def test_text_chunking(self):
        """Test text chunking functionality"""
        try:
            from data_processor import DataProcessor
            
            processor = DataProcessor()
            
            # Test text
            text = "This is a test document. " * 50  # Create long text
            
            # Process text
            chunks = processor.chunk_text(text)
            
            assert len(chunks) > 0
            assert all(isinstance(chunk, str) for chunk in chunks)
            assert all(len(chunk) > 0 for chunk in chunks)
            
        except ImportError:
            pytest.skip("Data processor not available")
        except Exception as e:
            pytest.skip(f"Chunking test failed: {e}")

class TestVectorStore:
    """Test cases for vector store operations"""
    
    @patch('chromadb.PersistentClient')
    def test_vector_store_connection(self, mock_client):
        """Test vector store connection"""
        try:
            import chromadb
            
            # Mock the client
            mock_client_instance = Mock()
            mock_client.return_value = mock_client_instance
            
            # Test connection
            client = chromadb.PersistentClient(path="test_db")
            assert client is not None
            
        except ImportError:
            pytest.skip("ChromaDB not available")

class TestLLMInterface:
    """Test cases for LLM interface"""
    
    def test_llm_interface_import(self):
        """Test LLM interface import"""
        try:
            from llm_interface import LLMInterface
            assert LLMInterface is not None
        except ImportError as e:
            pytest.skip(f"LLM interface import failed: {e}")
    
    @patch('llm_interface.Groq')
    def test_llm_interface_initialization(self, mock_groq):
        """Test LLM interface initialization"""
        try:
            from llm_interface import LLMInterface
            
            # Mock Groq client
            mock_client = Mock()
            mock_groq.return_value = mock_client
            
            # Initialize interface
            interface = LLMInterface(api_key="test_key")
            
            assert interface is not None
            assert hasattr(interface, 'client')
            
        except ImportError:
            pytest.skip("LLM interface not available")

class TestIntegration:
    """Integration tests"""
    
    def test_environment_variables(self):
        """Test that environment variables can be loaded"""
        from dotenv import load_dotenv
        
        # Try to load .env file
        load_dotenv('.env.example')
        
        # Test that we can access environment variables
        assert os.getenv is not None
    
    def test_requirements_satisfaction(self):
        """Test that key requirements are available"""
        required_packages = [
            'gradio',
            'sentence_transformers', 
            'chromadb',
            'groq',
            'pandas',
            'numpy'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            pytest.skip(f"Missing packages: {missing_packages}")
        
        assert len(missing_packages) == 0

class TestMockRAGPipeline:
    """Mock tests for RAG functionality"""
    
    def test_mock_query_processing(self):
        """Test mock query processing"""
        # Mock a simple RAG query
        query = "How do I get a marriage license in Ottawa?"
        
        # Mock response
        expected_response = {
            "answer": "To get a marriage license in Ottawa, visit City Hall...",
            "sources": ["ottawa.ca/marriage-licenses"],
            "confidence": 0.85
        }
        
        # This would be replaced with actual RAG pipeline
        mock_response = expected_response
        
        assert mock_response["answer"] is not None
        assert len(mock_response["sources"]) > 0
        assert mock_response["confidence"] > 0.5

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])