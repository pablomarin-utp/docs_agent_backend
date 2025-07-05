import logging, sys
from uuid import uuid4
from langchain.tools import tool, StructuredTool
from typing import Dict, Any, List
from app.config.qdrant import qdrant_client
from app.config.embeddings import embedding_model
from app.schemas.tools_schema import AddDocumentsArgs
logger = logging.getLogger(__name__)

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
    
    """Add documents to a specified collection in Qdrant."""

    if not documents:
        return {"error": "No documents to add."}

    logger.info(f"Adding {len(documents)} documents to collection: {collection_name}")
    
    try:
        vectors = embedding_model.embed_documents(documents)  # Batch embeddings
        points = [
            {"id": str(uuid4()), "vector": vec, "payload": {"text": doc}}
            for doc, vec in zip(documents, vectors)
        ]

        qdrant_client.upsert(
            collection_name=collection_name,
            points=points
        )
        return {"result": f"{len(points)} documents added to '{collection_name}'."}
    
    except Exception as e:
        logger.error(f"Error adding documents: {e}")
        return {"error": str(e)}


