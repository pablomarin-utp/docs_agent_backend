from PyPDF2 import PdfReader
from typing import List
import tiktoken
from langchain_core.tools import tool
from app.schemas.tools_schema import PDFChunkerArgs

@tool(args_schema=PDFChunkerArgs)
def pdf_to_chunks(file_path: str, max_pages: int = 15, max_tokens_per_chunk: int = 650) -> List[str]:
    """
    Carga un PDF desde ruta y lo divide en chunks de máximo `max_tokens_per_chunk` tokens.
    Solo toma las primeras `max_pages` páginas.
    """

    # Leer PDF
    reader = PdfReader(file_path)
    pages = reader.pages[:max_pages]  # limitar a N páginas
    
    # Extraer texto
    full_text = "\n".join(page.extract_text() or "" for page in pages)

    # Tokenizador OpenAI (usa el del modelo de embeddings)
    tokenizer = tiktoken.get_encoding("cl100k_base")

    # Chunking
    words = full_text.split()
    chunks = []
    chunk = []
    token_count = 0

    for word in words:
        word_tokens = len(tokenizer.encode(word, disallowed_special=()))
        if token_count + word_tokens > max_tokens_per_chunk:
            chunks.append(" ".join(chunk))
            chunk = []
            token_count = 0
        chunk.append(word)
        token_count += word_tokens

    if chunk:
        chunks.append(" ".join(chunk))

    return chunks

