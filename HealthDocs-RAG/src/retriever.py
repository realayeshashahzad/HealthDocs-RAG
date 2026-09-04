# ============================================================
# HealthDocs RAG - Retriever
# ============================================================

from config import TOP_K


def create_retriever(vector_store):
    """
    Create a retriever from the vector store.
    """

    retriever = vector_store.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": TOP_K
        }
    )

    return retriever