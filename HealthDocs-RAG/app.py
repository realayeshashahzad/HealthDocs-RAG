import os
import tempfile
import streamlit as st

from config import APP_TITLE, APP_ICON, SUPPORTED_FILE_TYPES

from src.document_loader import load_document
from src.text_splitter import split_documents
from src.embeddings import create_embeddings
from src.vector_store import create_vector_store
from src.retriever import create_retriever
from src.rag_chain import create_llm, ask_question


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide"
)


# ============================================================
# SESSION STATE
# ============================================================

if "api_key" not in st.session_state:
    st.session_state.api_key = None

if "llm" not in st.session_state:
    st.session_state.llm = None

if "retriever" not in st.session_state:
    st.session_state.retriever = None

if "vector_store" not in st.session_state:
    st.session_state.vector_store = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# ============================================================
# FIRST SCREEN — API KEY
# ============================================================

if not st.session_state.api_key:

    st.title("🏥 HealthDocs RAG")

    st.markdown(
        "## 🔐 Enter Your OpenAI API Key"
    )

    st.write(
        "Please enter your own OpenAI API key to continue."
    )

    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        placeholder="sk-..."
    )

    if st.button(
        "🚀 Continue",
        use_container_width=True
    ):

        if not api_key.strip():

            st.error(
                "❌ Please enter your OpenAI API key."
            )

        else:

            try:

                # Test/create LLM with user's key
                llm = create_llm(
                    api_key.strip()
                )

                st.session_state.api_key = (
                    api_key.strip()
                )

                st.session_state.llm = llm

                st.success(
                    "✅ API key accepted!"
                )

                st.rerun()

            except Exception:

                st.error(
                    "❌ Invalid or unavailable API key. "
                    "Please check your key and try again."
                )

    st.info(
        "🔒 Your API key is entered by you and is not "
        "stored in the source code."
    )

    st.stop()


# ============================================================
# MAIN HEALTHDOCS INTERFACE
# ============================================================

st.title("🏥 HealthDocs RAG")

st.markdown(
    "### AI-Powered Document-Grounded Health Information Assistant"
)

st.caption(
    "Upload trusted educational health documents "
    "and ask questions based on their content."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("📚 HealthDocs")

st.sidebar.success(
    "🟢 API Connected"
)

if st.sidebar.button(
    "🔑 Change API Key",
    use_container_width=True
):

    st.session_state.api_key = None
    st.session_state.llm = None
    st.session_state.retriever = None
    st.session_state.vector_store = None

    st.rerun()


# ============================================================
# DOCUMENT UPLOAD
# ============================================================

st.sidebar.header("📄 Upload Documents")

uploaded_files = st.sidebar.file_uploader(
    "Choose health documents",
    type=SUPPORTED_FILE_TYPES,
    accept_multiple_files=True
)


# ============================================================
# PROCESS DOCUMENTS
# ============================================================

if uploaded_files:

    if st.sidebar.button(
        "🚀 Process Documents",
        use_container_width=True
    ):

        all_documents = []

        progress = st.progress(0)

        for index, uploaded_file in enumerate(
            uploaded_files
        ):

            suffix = os.path.splitext(
                uploaded_file.name
            )[1]

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix
            ) as temp_file:

                temp_file.write(
                    uploaded_file.getbuffer()
                )

                temp_path = temp_file.name

            try:

                documents = load_document(
                    temp_path
                )

                for document in documents:

                    document.metadata["source"] = (
                        uploaded_file.name
                    )

                all_documents.extend(
                    documents
                )

            finally:

                os.remove(temp_path)

            progress.progress(
                (index + 1) / len(uploaded_files)
            )


        # ====================================================
        # CREATE RAG
        # ====================================================

        if all_documents:

            with st.spinner(
                "🧠 Creating knowledge base..."
            ):

                chunks = split_documents(
                    all_documents
                )

                embeddings = create_embeddings(
                    st.session_state.api_key
                )

                vector_store = create_vector_store(
                    chunks,
                    embeddings
                )

                retriever = create_retriever(
                    vector_store
                )

                st.session_state.vector_store = (
                    vector_store
                )

                st.session_state.retriever = (
                    retriever
                )

            st.success(
                "✅ Documents processed successfully!"
            )

            st.info(
                f"📊 Created {len(chunks)} searchable chunks."
            )


# ============================================================
# KNOWLEDGE BASE STATUS
# ============================================================

if st.session_state.retriever:

    st.sidebar.success(
        "🟢 Knowledge Base Ready"
    )

else:

    st.sidebar.info(
        "Upload and process documents first."
    )


# ============================================================
# CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask something about your health documents..."
)


if question:

    if st.session_state.retriever is None:

        st.warning(
            "⚠️ Please upload and process documents first."
        )

        st.stop()


    # USER MESSAGE

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):

        st.markdown(question)


    # AI RESPONSE

    with st.chat_message("assistant"):

        with st.spinner(
            "🔎 Searching your documents..."
        ):

            try:

                answer, source_documents = ask_question(
                    question,
                    st.session_state.retriever,
                    st.session_state.llm
                )

                st.markdown(answer)


                # ==========================================
                # SOURCES
                # ==========================================

                if source_documents:

                    st.markdown(
                        "### 📚 Sources"
                    )

                    displayed_sources = set()

                    for document in source_documents:

                        source = document.metadata.get(
                            "source",
                            "Unknown"
                        )

                        page = document.metadata.get(
                            "page",
                            None
                        )

                        if page is not None:

                            source_text = (
                                f"📄 {source} — "
                                f"Page {page + 1}"
                            )

                        else:

                            source_text = (
                                f"📄 {source}"
                            )

                        if source_text not in displayed_sources:

                            st.caption(
                                source_text
                            )

                            displayed_sources.add(
                                source_text
                            )


            except Exception as e:

                st.error(
                    f"❌ Error: {str(e)}"
                )

                answer = (
                    "I was unable to process your question."
                )


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


# ============================================================
# DISCLAIMER
# ============================================================

st.divider()

st.caption(
    "⚠️ Educational use only. HealthDocs RAG provides "
    "information based on uploaded documents. It does not "
    "diagnose medical conditions or replace advice from "
    "a qualified healthcare professional."
)