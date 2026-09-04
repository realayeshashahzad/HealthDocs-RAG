# ============================================================
# HealthDocs RAG - RAG Chain
# ============================================================

from langchain_openai import ChatOpenAI

from config import OPENAI_MODEL
from src.prompts import SYSTEM_PROMPT


def create_llm(api_key):
    """
    Create the OpenAI chat model using the user's API key.
    """

    if not api_key:
        raise ValueError("OpenAI API key is required.")

    llm = ChatOpenAI(
        api_key=api_key,
        model=OPENAI_MODEL,
        temperature=0
    )

    return llm


def format_context(documents):
    """
    Format retrieved documents into context text.
    """

    context_parts = []

    for doc in documents:

        source = doc.metadata.get(
            "source",
            "Unknown source"
        )

        page = doc.metadata.get(
            "page",
            None
        )

        if page is not None:
            page_number = page + 1
            source_info = f"{source} | Page {page_number}"
        else:
            source_info = source

        context_parts.append(
            f"Source: {source_info}\n"
            f"{doc.page_content}"
        )

    return "\n\n---\n\n".join(context_parts)


def ask_question(question, retriever, llm):
    """
    Retrieve relevant documents and generate an answer.
    """

    documents = retriever.invoke(question)

    if not documents:
        return (
            "I could not find relevant information in "
            "the uploaded documents."
        ), []

    context = format_context(documents)

    prompt = SYSTEM_PROMPT.format(
        context=context,
        question=question
    )

    response = llm.invoke(prompt)

    return response.content, documents