import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
from openai import OpenAI
from fastapi import HTTPException


from config import get_settings

settings = get_settings()


class VectorService:
    """
    Service to handle embeddings and vector search with ChromaDB.
    """
    
    def __init__(self, collection_name: str = "documents"):
        """
        Initializes the vector service.
        
        Args:
            collection_name: ChromaDB collection name (allows multiple collections)
        """
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        self.openai_client = None
        self.embedding_model = settings.OPENAI_EMBEDDING_MODEL
        
        self._initialize_clients()
    
    def _initialize_clients(self) -> None:
        """Initializes ChromaDB and OpenAI clients."""
        try:
            # Configure ChromaDB - use path from configuration
            chroma_db_path = settings.CHROMA_DB_PATH
            Path(chroma_db_path).mkdir(parents=True, exist_ok=True)
            
            # Use OpenAI embedding function
            embedding_function = embedding_functions.OpenAIEmbeddingFunction(
                api_key=settings.OPENAI_API_KEY,
                model_name=self.embedding_model
            )
            
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(
                path=chroma_db_path,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=embedding_function,
                metadata={"description": "Document chunks embeddings"}
            )
            
            # Initialize OpenAI client
            self.openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error initializing VectorService: {str(e)}"
            )
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generates an embedding for text using OpenAI.
        
        Args:
            text: Text to convert to embedding
            
        Returns:
            List of floats representing the embedding
        """
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating embedding: {str(e)}"
            )
    
    def add_chunks(
        self,
        chunks: List[Dict[str, Any]],
        document_id: int
    ) -> None:
        """
        Adds multiple chunks to ChromaDB with their embeddings.
        
        Args:
            chunks: List of dictionaries with 'id' and 'text' for each chunk
            document_id: ID of the document the chunks belong to
        """
        try:
            if not chunks:
                return
            
            # Prepare data for ChromaDB
            ids = [f"chunk_{chunk['id']}" for chunk in chunks]
            texts = [chunk['text'] for chunk in chunks]
            metadatas = [
                {
                    "chunk_id": chunk['id'],
                    "document_id": document_id,
                    "text": chunk['text'][:100]  # First 100 characters for metadata
                }
                for chunk in chunks
            ]
            
            # Add to ChromaDB (automatically generates embeddings)
            self.collection.add(
                ids=ids,
                documents=texts,
                metadatas=metadatas
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error adding chunks to ChromaDB: {str(e)}"
            )
    
    def search_similar_chunks(
        self,
        query: str,
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Searches for similar chunks to a query using vector search.
        
        Args:
            query: Query text
            n_results: Number of results to return
            filter_metadata: Optional metadata filters (e.g., {"document_id": 1})
            
        Returns:
            List of similar chunks with their metadata and scores
        """
        try:
            # Perform search in ChromaDB
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=filter_metadata if filter_metadata else None
            )
            
            # Format results
            similar_chunks = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    chunk_id = results['ids'][0][i]
                    metadata = results['metadatas'][0][i]
                    distance = results['distances'][0][i] if 'distances' in results else None
                    
                    similar_chunks.append({
                        "chunk_id": metadata.get("chunk_id"),
                        "document_id": metadata.get("document_id"),
                        "text": results['documents'][0][i],
                        "score": 1 - distance if distance else None,  # Convert distance to score
                        "metadata": metadata
                    })
            
            return similar_chunks
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error searching for similar chunks: {str(e)}"
            )
    
    def delete_document_chunks(self, document_id: int) -> None:
        """
        Deletes all chunks of a document from ChromaDB.
        
        Args:
            document_id: ID of the document whose chunks will be deleted
        """
        try:
            # Find all chunks of the document
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if results['ids']:
                # Delete chunks
                self.collection.delete(ids=results['ids'])
                
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting document chunks: {str(e)}"
            )
    
    def get_collection_info(self) -> Dict[str, Any]:
        """
        Gets information about the current collection.
        
        Returns:
            Dictionary with collection information
        """
        try:
            count = self.collection.count()
            return {
                "collection_name": self.collection_name,
                "total_chunks": count,
                "embedding_model": self.embedding_model
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting collection information: {str(e)}"
            )


# Singleton instance for global use
_vector_service_instance: Optional[VectorService] = None


def get_vector_service(collection_name: str = "documents") -> VectorService:
    """
    Gets an instance of the vector service (singleton pattern).
    
    Args:
        collection_name: Collection name to use
        
    Returns:
        VectorService instance
    """
    global _vector_service_instance
    
    if _vector_service_instance is None or _vector_service_instance.collection_name != collection_name:
        _vector_service_instance = VectorService(collection_name=collection_name)
    
    return _vector_service_instance

