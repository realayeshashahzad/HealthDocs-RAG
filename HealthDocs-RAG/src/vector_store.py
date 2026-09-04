# ============================================================
# HealthDocs RAG - Vector Store
# ============================================================

from langchain_community.vectorstores import FAISS


def create_vector_store(documents, embeddings):
    """
    Create a FAISS vector store from document chunks.
    """

    if not documents:
        raise ValueError(
            "No document chunks were provided."
        )

    vector_store = FAISS.from_documents(
        documents,
        embeddings
    )

    return vector_store