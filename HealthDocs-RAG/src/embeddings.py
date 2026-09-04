# ============================================================
# HealthDocs RAG - Embeddings
# ============================================================

from langchain_openai import OpenAIEmbeddings

from config import EMBEDDING_MODEL


def create_embeddings(api_key):
    """
    Create OpenAI embeddings using the user's API key.
    """

    if not api_key:
        raise ValueError("OpenAI API key is required.")

    embeddings = OpenAIEmbeddings(
        api_key=api_key,
        model=EMBEDDING_MODEL
    )

    return embeddings