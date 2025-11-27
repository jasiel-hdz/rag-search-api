"""
RAG (Retrieval Augmented Generation) service for semantic search.
Uses ChromaDB for vector search and LLM to generate responses.
"""

from typing import List, Dict, Any, Optional
from fastapi import HTTPException

from core.vector.service import get_vector_service
from core.llm.services import llm_service
from core.rag.schema import RAGQueryRequest, RAGQueryResponse, ChunkResult
from config import get_settings

settings = get_settings()


class RAGService:
    """
    Service for RAG search using embeddings and LLM.
    """
    
    def __init__(self):
        self.vector_service = get_vector_service()
        self.llm_service = llm_service
    
    def search_and_generate(self, request: RAGQueryRequest) -> RAGQueryResponse:
        """
        Searches for similar chunks and generates a response using the LLM.
        
        Args:
            request: RAGQueryRequest object with query and parameters
            
        Returns:
            RAGQueryResponse with found chunks and generated response
            
        Raises:
            HTTPException: If an error occurs during search or generation
        """
        try:
            # Filter by document if specified
            filter_metadata = None
            if request.document_id:
                filter_metadata = {"document_id": request.document_id}
            
            # Search for similar chunks using vector search
            # n_results comes from configuration, not from user
            similar_chunks = self.vector_service.search_similar_chunks(
                query=request.query,
                n_results=settings.RAG_N_RESULTS,
                filter_metadata=filter_metadata
            )
            
            # Build context from found chunks
            context = self._build_context(similar_chunks)
            
            # Generate response using LLM
            prompt = self._build_prompt(request.query, context)
            response = self.llm_service.generate_response(prompt)
            
            # Format chunks for response
            chunk_results = [
                ChunkResult(
                    chunk_id=chunk.get("chunk_id"),
                    document_id=chunk.get("document_id"),
                    text=chunk.get("text", ""),
                    score=chunk.get("score"),
                    metadata=chunk.get("metadata", {})
                )
                for chunk in similar_chunks
            ]
            
            return RAGQueryResponse(
                query=request.query,
                chunks_found=len(similar_chunks),
                chunks=chunk_results,
                response=response,
                context_used=context if len(similar_chunks) > 0 else None
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error in RAG search: {str(e)}"
            )
    
    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Builds context from found chunks.
        
        Args:
            chunks: List of similar chunks
            
        Returns:
            String with formatted context
        """
        if not chunks:
            return "No relevant information found."
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Chunk {i} - Document {chunk.get('document_id', 'N/A')}]:\n"
                f"{chunk.get('text', '')}\n"
            )
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, query: str, context: str) -> str:
        """
        Builds the prompt for the LLM with query and context.
        
        Args:
            query: User query
            context: Context extracted from chunks
            
        Returns:
            Formatted prompt for the LLM
        """
        return f"""Based on the following information, answer the user's question.
If the information is not sufficient or not related, clearly indicate so.

Available information:
{context}

User question: {query}

Answer:"""

