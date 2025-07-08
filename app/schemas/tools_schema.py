from typing import Optional, List
from pydantic import BaseModel, Field
from typing_extensions import Annotated
from langgraph.graph.message import add_messages

class RAGQueryInput(BaseModel):
    """Input schema for RAG (Retrieval-Augmented Generation) queries."""
    query: str = Field(..., description="Query text for searching relevant documents")
    top_k: Optional[int] = Field(default=5, description="Maximum number of documents to retrieve")
    collection: str = Field(..., description="Name of the Qdrant collection to search documents")

class RagSearchArgs(BaseModel):
    """Arguments for RAG search tool."""
    query: str
    collection: str
    top_k: int = 3

class PDFChunkerArgs(BaseModel):
    """Arguments for PDF chunking tool."""
    file_path: str = Field(..., description="Path to the PDF file to process")
    max_pages: int = Field(default=15, description="Maximum number of pages to process from PDF")
    max_tokens_per_chunk: int = Field(default=650, description="Maximum number of tokens per chunk")

class AddDocumentsArgs(BaseModel):
    """Arguments for adding documents to a collection."""
    collection_name: str = Field(..., description="Name of the Qdrant collection")
    documents: List[str] = Field(..., description="List of documents to add to the collection")
