import logging, sys
from uuid import uuid4
from langchain.tools import tool
from typing import Dict, Any, List
from app.config.qdrant import qdrant_client
from app.config.embeddings import embedding_model
from app.schemas.tools_schema import AddDocumentsArgs
from app.utils.logging_utils import get_secure_logger

logger = get_secure_logger(__name__)

def logger_setup():
    """
    Set up logger configuration for the application.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log", mode='a')
        ]
    )
    logging.info("logger setup complete.")

@tool
def add_documents_tool(
    collection_name: str,
    documents: List[str]
) -> Dict[str, Any]:
    """
    Add documents to a specified Qdrant collection.
    
    Args:
        collection_name: Name of the Qdrant collection
        documents: List of document texts to add
        
    Returns:
        Dictionary with result message or error
    """
    logger.info("Adding documents to collection", collection_name=collection_name, document_count=len(documents))

    if not documents:
        logger.warning("No documents provided for addition", collection_name=collection_name)
        return {"error": "No documents to add."}

    try:
        # Generate embeddings for all documents
        vectors = embedding_model.embed_documents(documents)
        logger.debug("Document embeddings generated", collection_name=collection_name, vector_count=len(vectors))
        
        # Create points for Qdrant
        points = [
            {"id": str(uuid4()), "vector": vec, "payload": {"text": doc}}
            for doc, vec in zip(documents, vectors)
        ]

        # Upsert points to collection
        qdrant_client.upsert(
            collection_name=collection_name,
            points=points
        )
        
        logger.info("Documents added successfully", collection_name=collection_name, documents_added=len(points))
        return {"result": f"{len(points)} documents added to '{collection_name}'."}
    
    except Exception as e:
        logger.error("Error adding documents", collection_name=collection_name, error=str(e))
        return {"error": str(e)}


