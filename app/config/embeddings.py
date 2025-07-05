from langchain_openai import AzureOpenAIEmbeddings
from app.config.load import (
    AZURE_OPENAI_EMBEDDINGS_API_KEY,
    AZURE_OPENAI_EMBEDDINGS_ENDPOINT,
    AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME,
    AZURE_OPENAI_API_VERSION,
)

embedding_model = AzureOpenAIEmbeddings(
    openai_api_key=AZURE_OPENAI_EMBEDDINGS_API_KEY,
    azure_endpoint=AZURE_OPENAI_EMBEDDINGS_ENDPOINT,
    deployment=AZURE_OPENAI_EMBEDDINGS_DEPLOYMENT_NAME,
    openai_api_version=AZURE_OPENAI_API_VERSION,
)
