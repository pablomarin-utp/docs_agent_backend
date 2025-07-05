import logging, sys
from langchain.tools import tool
from typing import List
from app.config.qdrant import qdrant_client

logger = logging.getLogger(__name__)

@tool
def get_collections_tool() -> List[str]:
    """
    Retrieve the list of collections from the Qdrant client.
    
    Returns:
        List[str]: A list of collection names.
    """
    try:
        collections = qdrant_client.get_collections() #returns a tuple 
        return [collection.name for collection in collections.collections]  # Assuming collections[0] is the response object
    except Exception as e:
        logger.error(f"Error retrieving collections: {e}")
        logger.error(f"Returns a tuple like this: {collections}")
        return []
