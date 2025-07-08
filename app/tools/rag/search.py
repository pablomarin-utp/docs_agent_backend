import logging
from langchain.tools import tool
from typing import Dict, Any, List
from app.config.qdrant import qdrant_client 
from app.schemas.tools_schema import RAGQueryInput, RagSearchArgs
from app.config.embeddings import embedding_model
from langchain_core.messages import ToolMessage
from app.utils.logging_utils import get_secure_logger

logger = get_secure_logger(__name__)

@tool(args_schema=RAGQueryInput)
def rag_qdrant_search(query: str, collection: str, top_k: int = 5) -> str:
    """
    Perform semantic search on a Qdrant vector database collection.
    
    Args:
        query: Search query text
        collection: Name of the Qdrant collection to search
        top_k: Maximum number of results to return
        
    Returns:
        Combined text from relevant documents found in the collection
    """
    logger.info("Executing RAG search", query=query, collection=collection, top_k=top_k)
    
    try:
        query_vector = embedding_model.embed_query(query)
        logger.debug("Query vector generated successfully", collection=collection)
        
        results = qdrant_client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True
        )
        
        logger.debug("Qdrant search completed", collection=collection, results_count=len(results))
        
        docs_text: List[str] = [
            result.payload.get("text", "") 
            for result in results 
            if result.payload.get("text")
        ]
        
        if not docs_text:
            logger.warning("No relevant documents found", query=query, collection=collection)
            return "No relevant documents found for this query in the specified collection."
        
        logger.info("RAG search completed successfully", collection=collection, docs_found=len(docs_text))
        return "\n\n".join(docs_text)
        
    except Exception as e:
        logger.error("RAG search failed", query=query, collection=collection, error=str(e))
        return f"Search error: {str(e)}"

# --- DEPRECATED FUNCTIONS ---

def rag_qdrant_search_deprecated(params: RAGQueryInput) -> ToolMessage:
    """
    DEPRECATED: Legacy RAG search function.
    
    Args:
        params: RAG query input parameters including query, collection, and top_k
        
    Returns:
        Combined text from search results
    """
    
    logger.info(f"Received RAG query: {params.query} with top_k={params.top_k}")
    logger.debug(f"Query type: {type(params.query)}, value: {params.query}")

    query_vector = embedding_model.embed_query(params.query)
    logger.debug(f"Query vector generated: {query_vector[:5]}... (truncated)")
    
    results = qdrant_client.search(
        collection_name=params.collection,
        query_vector=query_vector,
        limit=params.top_k,
        with_payload=True
    )
    
    logger.info(f"Search results: {len(results)} documents found")
    docs_text: List[str] = [result.payload.get("text", "") for result in results if result.payload.get("text")]

    if not docs_text:
        logger.debug("No relevant documents found in search results")
        return str("No relevant documents found for the query.")
    
    logger.debug(f"Documents found: {len(docs_text)}")
    combined_text = "\n\n".join(docs_text)
    return str(combined_text)
