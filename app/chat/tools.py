# List of available tools for the chat agent
from app.tools.rag.search import rag_qdrant_search
from app.tools.rag.add_documents import add_documents_tool
from app.tools.rag.create_collection import create_collection_tool
from app.tools.rag.pdf_chunker import pdf_to_chunks
from app.tools.rag.get_collections import get_collections_tool

# Available tools for the LangChain agent
tools_list = [
    rag_qdrant_search,
    add_documents_tool,
    create_collection_tool,
    pdf_to_chunks,
    get_collections_tool
]