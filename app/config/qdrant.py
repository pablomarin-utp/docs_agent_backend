from qdrant_client import QdrantClient
from app.config.load import QDRANT_URL, QDRANT_API_KEY

qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY
)
