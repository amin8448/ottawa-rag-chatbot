"""
Embedding Manager for Ottawa RAG Pipeline
Handles SentenceTransformer embeddings with optimization for large datasets
"""

import numpy as np
from typing import List, Union, Optional
import logging
from pathlib import Path
import pickle
import hashlib

from sentence_transformers import SentenceTransformer
import torch

class EmbeddingManager:
    """
    Manages text embeddings using SentenceTransformers
    
    Features:
    - Batch processing for large datasets
    - GPU acceleration when available
    - Embedding caching for faster reloads
    - Multiple model support
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        cache_dir: Optional[str] = "data/embeddings/cache",
        device: Optional[str] = None,
        batch_size: int = 32
    ):
        """
        Initialize the embedding manager
        
        Args:
            model_name: HuggingFace model name for embeddings
            cache_dir: Directory to cache embeddings
            device: Device to run on ('cpu', 'cuda', or None for auto)
            batch_size: Batch size for processing large datasets
        """
        self.model_name = model_name
        self.batch_size = batch_size
        self.cache_dir = Path(cache_dir) if cache_dir else None
        
        # Setup device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        # Initialize model
        self._setup_logging()
        self._load_model()
        self._setup_cache()
        
    def _setup_logging(self):
        """Setup logging for embedding operations"""
        self.logger = logging.getLogger(__name__)
        
    def _load_model(self):
        """Load the SentenceTransformer model"""
        try:
            self.logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name, device=self.device)
            self.embedding_dimension = self.model.get_sentence_embedding_dimension()
            self.logger.info(f"Model loaded successfully. Embedding dimension: {self.embedding_dimension}")
            
        except Exception as e:
            self.logger.error(f"Error loading model {self.model_name}: {e}")
            raise
    
    def _setup_cache(self):
        """Setup embedding cache directory"""
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Embedding cache directory: {self.cache_dir}")
    
    def generate_embeddings(
        self, 
        texts: List[str], 
        use_cache: bool = True,
        show_progress: bool = True
    ) -> np.ndarray:
        """
        Generate embeddings for a list of texts
        
        Args:
            texts: List of text strings to embed
            use_cache: Whether to use cached embeddings
            show_progress: Show progress bar for large batches
            
        Returns:
            NumPy array of embeddings (n_texts, embedding_dim)
        """
        try:
            if not texts:
                return np.array([])
            
            # Check cache first
            if use_cache and self.cache_dir:
                cached_embeddings = self._load_from_cache(texts)
                if cached_embeddings is not None:
                    self.logger.info("Loaded embeddings from cache")
                    return cached_embeddings
            
            self.logger.info(f"Generating embeddings for {len(texts)} texts...")
            
            # Generate embeddings in batches for memory efficiency
            all_embeddings = []
            
            for i in range(0, len(texts), self.batch_size):
                batch_texts = texts[i:i + self.batch_size]
                
                if show_progress:
                    self.logger.info(f"Processing batch {i//self.batch_size + 1}/{(len(texts)-1)//self.batch_size + 1}")
                
                # Generate embeddings for batch
                batch_embeddings = self.model.encode(
                    batch_texts,
                    convert_to_numpy=True,
                    show_progress_bar=False,  # Manage progress manually
                    batch_size=min(self.batch_size, len(batch_texts))
                )
                
                all_embeddings.append(batch_embeddings)
            
            # Combine all batches
            embeddings = np.vstack(all_embeddings)
            
            # Cache the embeddings
            if use_cache and self.cache_dir:
                self._save_to_cache(texts, embeddings)
            
            self.logger.info(f"Generated embeddings shape: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {e}")
            raise
    
    def generate_single_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text (optimized for queries)
        
        Args:
            text: Single text string
            
        Returns:
            1D NumPy array embedding
        """
        try:
            embedding = self.model.encode([text], convert_to_numpy=True)[0]
            return embedding
            
        except Exception as e:
            self.logger.error(f"Error generating single embedding: {e}")
            raise
    
    def compute_similarity(
        self, 
        query_embedding: np.ndarray, 
        document_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Compute cosine similarity between query and document embeddings
        
        Args:
            query_embedding: Single query embedding (1D array)
            document_embeddings: Document embeddings (2D array)
            
        Returns:
            Similarity scores (1D array)
        """
        try:
            # Normalize embeddings
            query_norm = query_embedding / np.linalg.norm(query_embedding)
            doc_norms = document_embeddings / np.linalg.norm(document_embeddings, axis=1, keepdims=True)
            
            # Compute cosine similarity
            similarities = np.dot(doc_norms, query_norm)
            
            return similarities
            
        except Exception as e:
            self.logger.error(f"Error computing similarity: {e}")
            raise
    
    def _generate_cache_key(self, texts: List[str]) -> str:
        """Generate a cache key for a list of texts"""
        # Create hash from concatenated texts and model name
        combined_text = "|".join(texts) + f"|{self.model_name}"
        cache_key = hashlib.sha256(combined_text.encode()).hexdigest()[:16]
        return cache_key
    
    def _load_from_cache(self, texts: List[str]) -> Optional[np.ndarray]:
        """Load embeddings from cache if available"""
        try:
            cache_key = self._generate_cache_key(texts)
            cache_file = self.cache_dir / f"embeddings_{cache_key}.pkl"
            
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    cached_data = pickle.load(f)
                
                # Verify the cached data matches our texts
                if (cached_data.get('model_name') == self.model_name and 
                    cached_data.get('text_count') == len(texts)):
                    return cached_data['embeddings']
            
            return None
            
        except Exception as e:
            self.logger.warning(f"Error loading from cache: {e}")
            return None
    
    def _save_to_cache(self, texts: List[str], embeddings: np.ndarray):
        """Save embeddings to cache"""
        try:
            cache_key = self._generate_cache_key(texts)
            cache_file = self.cache_dir / f"embeddings_{cache_key}.pkl"
            
            cache_data = {
                'model_name': self.model_name,
                'text_count': len(texts),
                'embeddings': embeddings,
                'embedding_dimension': self.embedding_dimension
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            self.logger.info(f"Saved embeddings to cache: {cache_file}")
            
        except Exception as e:
            self.logger.warning(f"Error saving to cache: {e}")
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model"""
        return {
            'model_name': self.model_name,
            'embedding_dimension': self.embedding_dimension,
            'device': self.device,
            'batch_size': self.batch_size,
            'cache_enabled': self.cache_dir is not None,
            'cache_dir': str(self.cache_dir) if self.cache_dir else None
        }
    
    def clear_cache(self):
        """Clear all cached embeddings"""
        if self.cache_dir and self.cache_dir.exists():
            for cache_file in self.cache_dir.glob("embeddings_*.pkl"):
                cache_file.unlink()
            self.logger.info("Cleared embedding cache")
    
    def estimate_memory_usage(self, num_texts: int) -> dict:
        """Estimate memory usage for embedding generation"""
        embedding_size = self.embedding_dimension * 4  # 4 bytes per float32
        total_size = num_texts * embedding_size
        
        return {
            'texts': num_texts,
            'embedding_dimension': self.embedding_dimension,
            'size_per_embedding_mb': embedding_size / (1024 * 1024),
            'total_size_mb': total_size / (1024 * 1024),
            'recommended_batch_size': min(self.batch_size, max(1, int(1024 * 1024 * 100 / embedding_size)))  # 100MB batches
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize embedding manager
    embedding_manager = EmbeddingManager(
        model_name="all-MiniLM-L6-v2",
        cache_dir="data/embeddings/cache"
    )
    
    # Test with sample Ottawa content
    test_texts = [
        "How to apply for a marriage license in Ottawa",
        "Garbage collection schedule and recycling rules",
        "Parking regulations and violations in downtown Ottawa",
        "Fire safety requirements for backyard burning",
        "Business licensing and permit applications"
    ]
    
    # Generate embeddings
    embeddings = embedding_manager.generate_embeddings(test_texts)
    print(f"Generated embeddings shape: {embeddings.shape}")
    
    # Test single embedding (for queries)
    query = "marriage license requirements"
    query_embedding = embedding_manager.generate_single_embedding(query)
    print(f"Query embedding shape: {query_embedding.shape}")
    
    # Test similarity computation
    similarities = embedding_manager.compute_similarity(query_embedding, embeddings)
    print(f"Similarities: {similarities}")
    
    # Model information
    info = embedding_manager.get_model_info()
    print(f"Model info: {info}")
    
    # Memory estimation
    memory_est = embedding_manager.estimate_memory_usage(1410)  # Your chunk count
    print(f"Memory estimation for 1410 chunks: {memory_est}")