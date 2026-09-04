# ============================================================
# HealthDocs RAG - Configuration
# ============================================================

APP_TITLE = "HealthDocs RAG"
APP_ICON = "🏥"

# OpenAI model
OPENAI_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

# RAG settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
TOP_K = 4

# Supported document types
SUPPORTED_FILE_TYPES = ["pdf", "txt", "docx"]