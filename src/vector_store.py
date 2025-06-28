"""
Vector Store Manager for Ottawa RAG Pipeline
Handles ChromaDB operations with optimizations for large-scale retrieval
"""

import chromadb
from chromadb.config import Settings
import numpy as np
from typing import List, Dict, Any, Optional, Union
import logging
from pathlib import Path
import json
import uuid

class VectorStore:
    """
    Manages vector storage and retrieval using ChromaDB
    
    Features:
    - Persistent storage with ChromaDB
    - Efficient similarity search
    - Metadata filtering and management
    - Batch operations for large datasets
    - Collection management
    """
    
    def __init__(
        self,
        db_path: str = "data/embeddings/chroma_db",
        collection_name: str = "ottawa_complete",
        distance_metric: str = "cosine"
    ):
        """
        Initialize the vector store
        
        Args:
            db_path: Path to ChromaDB persistent storage
            collection_name: Name of the default collection
            distance_metric: Distance metric for similarity search ('cosine', 'l2', 'ip')
        """
        self.db_path = Path(db_path)
        self.collection_name = collection_name
        self.distance_metric = distance_metric
        
        # Initialize ChromaDB client
        self._setup_logging()
        self._initialize_client()
        self.current_collection = None
        
    def _setup_logging(self):
        """Setup logging for vector store operations"""
        self.logger = logging.getLogger(__name__)
        
    def _initialize_client(self):
        """Initialize ChromaDB client with persistent storage"""
        try:
            # Create database directory
            self.db_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=str(self.db_path),
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            self.logger.info(f"ChromaDB client initialized at: {self.db_path}")
            
        except Exception as e:
            self.logger.error(f"Error initializing ChromaDB client: {e}")
            raise
    
    def create_collection(
        self, 
        collection_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        overwrite: bool = False
    ) -> bool:
        """
        Create a new collection or get existing one
        
        Args:
            collection_name: Name of the collection
            metadata: Collection metadata
            overwrite: Whether to overwrite existing collection
            
        Returns:
            Success status
        """
        try:
            name = collection_name or self.collection_name
            
            # Delete existing collection if overwrite is True
            if overwrite:
                try:
                    self.client.delete_collection(name=name)
                    self.logger.info(f"Deleted existing collection: {name}")
                except:
                    pass  # Collection might not exist
            
            # Create or get collection
            try:
                self.current_collection = self.client.create_collection(
                    name=name,
                    metadata=metadata or {"description": "Ottawa city services documents"},
                    embedding_function=None  # We'll provide embeddings directly
                )
                self.logger.info(f"Created new collection: {name}")
            except Exception:
                # Collection might already exist
                self.current_collection = self.client.get_collection(name=name)
                self.logger.info(f"Using existing collection: {name}")
            
            self.collection_name = name
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating collection {name}: {e}")
            return False
    
    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: Union[List[List[float]], np.ndarray],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        batch_size: int = 1000
    ) -> bool:
        """
        Add documents to the vector store in batches
        
        Args:
            ids: Unique identifiers for documents
            documents: Text content of documents
            embeddings: Embedding vectors
            metadatas: Optional metadata for each document
            batch_size: Batch size for large insertions
            
        Returns:
            Success status
        """
        try:
            if not self.current_collection:
                self.logger.error("No collection selected. Call create_collection() first.")
                return False
            
            # Convert embeddings to list if numpy array
            if isinstance(embeddings, np.ndarray):
                embeddings = embeddings.tolist()
            
            # Ensure we have metadata for each document
            if metadatas is None:
                metadatas = [{"source": "ottawa.ca"} for _ in ids]
            
            # Validate input lengths
            if not (len(ids) == len(documents) == len(embeddings) == len(metadatas)):
                raise ValueError("All input lists must have the same length")
            
            self.logger.info(f"Adding {len(documents)} documents to collection")
            
            # Add documents in batches
            for i in range(0, len(documents), batch_size):
                end_idx = min(i + batch_size, len(documents))
                
                batch_ids = ids[i:end_idx]
                batch_documents = documents[i:end_idx]
                batch_embeddings = embeddings[i:end_idx]
                batch_metadatas = metadatas[i:end_idx]
                
                self.current_collection.add(
                    ids=batch_ids,
                    documents=batch_documents,
                    embeddings=batch_embeddings,
                    metadatas=batch_metadatas
                )
                
                self.logger.info(f"Added batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}")
            
            self.logger.info(f"Successfully added {len(documents)} documents")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding documents: {e}")
            return False
    
    def search(
        self,
        query_embedding: Union[List[float], np.ndarray],
        top_k: int = 5,
        where_filter: Optional[Dict[str, Any]] = None,
        include_distances: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using embedding
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            where_filter: Metadata filter conditions
            include_distances: Whether to include similarity scores
            
        Returns:
            List of search results with documents and metadata
        """
        try:
            if not self.current_collection:
                self.logger.error("No collection selected. Call create_collection() first.")
                return []
            
            # Convert numpy array to list if needed
            if isinstance(query_embedding, np.ndarray):
                query_embedding = query_embedding.tolist()
            
            # Perform search
            results = self.current_collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter,
                include=['documents', 'metadatas', 'distances'] if include_distances else ['documents', 'metadatas']
            )
            
            # Format results
            formatted_results = []
            documents = results['documents'][0] if results['documents'] else []
            metadatas = results['metadatas'][0] if results['metadatas'] else []
            distances = results['distances'][0] if include_distances and results.get('distances') else []
            
            for i, doc in enumerate(documents):
                result = {
                    'document': doc,
                    'metadata': metadatas[i] if i < len(metadatas) else {}
                }
                
                if include_distances and i < len(distances):
                    # Convert distance to similarity (assuming cosine distance)
                    similarity = 1 - distances[i] if self.distance_metric == 'cosine' else distances[i]
                    result['similarity'] = similarity
                    result['distance'] = distances[i]
                
                formatted_results.append(result)
            
            self.logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results
            
        except Exception as e:
            self.logger.error(f"Error searching documents: {e}")
            return []
    
    def search_by_text(
        self,
        query_text: str,
        top_k: int = 5,
        where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents using text query
        Note: This requires an embedding function to be set on the collection
        
        Args:
            query_text: Text query
            top_k: Number of results to return
            where_filter: Metadata filter conditions
            
        Returns:
            List of search results
        """
        try:
            if not self.current_collection:
                self.logger.error("No collection selected. Call create_collection() first.")
                return []
            
            # This method requires ChromaDB to have an embedding function
            # For our use case, we use search() with pre-computed embeddings
            self.logger.warning("Text search requires embedding function. Use search() with pre-computed embeddings.")
            return []
            
        except Exception as e:
            self.logger.error(f"Error in text search: {e}")
            return []
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the current collection"""
        try:
            if not self.current_collection:
                return {"error": "No collection selected"}
            
            # Get collection count
            count = self.current_collection.count()
            
            # Get collection metadata
            metadata = getattr(self.current_collection, 'metadata', {})
            
            return {
                "name": self.collection_name,
                "document_count": count,
                "metadata": metadata,
                "distance_metric": self.distance_metric,
                "db_path": str(self.db_path)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting collection info: {e}")
            return {"error": str(e)}
    
    def list_collections(self) -> List[str]:
        """List all available collections"""
        try:
            collections = self.client.list_collections()
            return [col.name for col in collections]
            
        except Exception as e:
            self.logger.error(f"Error listing collections: {e}")
            return []
    
    def delete_collection(self, collection_name: Optional[str] = None) -> bool:
        """Delete a collection"""
        try:
            name = collection_name or self.collection_name
            self.client.delete_collection(name=name)
            
            if name == self.collection_name:
                self.current_collection = None
            
            self.logger.info(f"Deleted collection: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting collection {name}: {e}")
            return False
    
    def update_document(
        self,
        doc_id: str,
        document: Optional[str] = None,
        embedding: Optional[Union[List[float], np.ndarray]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update a single document in the collection"""
        try:
            if not self.current_collection:
                self.logger.error("No collection selected. Call create_collection() first.")
                return False
            
            # Prepare update data
            update_data = {"ids": [doc_id]}
            
            if document is not None:
                update_data["documents"] = [document]
            
            if embedding is not None:
                if isinstance(embedding, np.ndarray):
                    embedding = embedding.tolist()
                update_data["embeddings"] = [embedding]
            
            if metadata is not None:
                update_data["metadatas"] = [metadata]
            
            # Update the document
            self.current_collection.update(**update_data)
            
            self.logger.info(f"Updated document: {doc_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating document {doc_id}: {e}")
            return False
    
    def delete_documents(self, doc_ids: List[str]) -> bool:
        """Delete documents from the collection"""
        try:
            if not self.current_collection:
                self.logger.error("No collection selected. Call create_collection() first.")
                return False
            
            self.current_collection.delete(ids=doc_ids)
            
            self.logger.info(f"Deleted {len(doc_ids)} documents")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting documents: {e}")
            return False
    
    def backup_collection(self, backup_path: str) -> bool:
        """Create a backup of the current collection"""
        try:
            if not self.current_collection:
                self.logger.error("No collection selected. Call create_collection() first.")
                return False
            
            # Get all documents from collection
            all_data = self.current_collection.get(
                include=['documents', 'metadatas', 'embeddings']
            )
            
            backup_data = {
                "collection_name": self.collection_name,
                "distance_metric": self.distance_metric,
                "data": all_data,
                "count": len(all_data['ids'])
            }
            
            # Save to JSON file
            backup_file = Path(backup_path)
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Backup created: {backup_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating backup: {e}")
            return False
    
    def restore_collection(self, backup_path: str, collection_name: Optional[str] = None) -> bool:
        """Restore collection from backup"""
        try:
            # Load backup data
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Create collection
            name = collection_name or backup_data['collection_name']
            self.create_collection(name, overwrite=True)
            
            # Restore data
            data = backup_data['data']
            if data['ids']:
                self.add_documents(
                    ids=data['ids'],
                    documents=data['documents'],
                    embeddings=data['embeddings'],
                    metadatas=data['metadatas']
                )
            
            self.logger.info(f"Restored collection from backup: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error restoring from backup: {e}")
            return False
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        try:
            collections = self.list_collections()
            total_documents = 0
            
            collection_stats = []
            for col_name in collections:
                try:
                    col = self.client.get_collection(col_name)
                    count = col.count()
                    total_documents += count
                    
                    collection_stats.append({
                        "name": col_name,
                        "document_count": count,
                        "metadata": getattr(col, 'metadata', {})
                    })
                except Exception:
                    continue
            
            return {
                "database_path": str(self.db_path),
                "total_collections": len(collections),
                "total_documents": total_documents,
                "collections": collection_stats,
                "current_collection": self.collection_name if self.current_collection else None
            }
            
        except Exception as e:
            self.logger.error(f"Error getting database stats: {e}")
            return {"error": str(e)}

# Example usage and testing
if __name__ == "__main__":
    # Initialize vector store
    vector_store = VectorStore(
        db_path="data/embeddings/chroma_db",
        collection_name="ottawa_test"
    )
    
    # Create test collection
    vector_store.create_collection("ottawa_test", overwrite=True)
    
    # Test data
    test_docs = [
        "How to apply for a marriage license in Ottawa",
        "Garbage collection schedule and recycling rules",
        "Parking regulations in downtown Ottawa"
    ]
    
    test_embeddings = np.random.rand(3, 384).tolist()  # Mock embeddings
    test_ids = [f"doc_{i}" for i in range(3)]
    test_metadata = [{"source": "ottawa.ca", "category": "services"} for _ in range(3)]
    
    # Add documents
    success = vector_store.add_documents(
        ids=test_ids,
        documents=test_docs,
        embeddings=test_embeddings,
        metadatas=test_metadata
    )
    print(f"Documents added: {success}")
    
    # Test search
    query_embedding = np.random.rand(384)
    results = vector_store.search(query_embedding, top_k=2)
    print(f"Search results: {len(results)}")
    
    # Collection info
    info = vector_store.get_collection_info()
    print(f"Collection info: {info}")
    
    # Database stats
    stats = vector_store.get_database_stats()
    print(f"Database stats: {stats}")