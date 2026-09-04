# ============================================================
# HealthDocs RAG - Document Loader
# ============================================================

import os

from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    Docx2txtLoader
)


def load_document(file_path):
    """
    Load a document based on its file extension.
    """

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        loader = PyPDFLoader(file_path)

    elif extension == ".txt":
        loader = TextLoader(
            file_path,
            encoding="utf-8"
        )

    elif extension == ".docx":
        loader = Docx2txtLoader(file_path)

    else:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    return loader.load()