# ==========================================
# AI LEARNSPHERE - APPLICATION SETTINGS
# ==========================================

# Application Information
APP_NAME = "AI LearnSphere"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = (
    "Intelligent Learning and Skill Development Platform"
)

# Supported Languages
SUPPORTED_LANGUAGES = [
    "English",
]

DEFAULT_LANGUAGE = "English"

# Learning Levels
LEARNING_LEVELS = [
    "Beginner",
    "Intermediate",
    "Advanced",
    "Auto-detect"
]

DEFAULT_LEARNING_LEVEL = "Auto-detect"

# Explanation Preferences
EXPLANATION_STYLES = [
    "Simple",
    "Detailed",
    "Both"
]

DEFAULT_EXPLANATION_STYLE = "Both"

# Quiz Settings
QUIZ_DIFFICULTIES = [
    "Beginner",
    "Intermediate",
    "Advanced"
]

DEFAULT_QUIZ_QUESTIONS = 10

AVAILABLE_QUESTION_COUNTS = [5, 10, 15, 20]

# AI Model Configuration
OLLAMA_BASE_URL = "http://localhost:11434"

DEFAULT_LLM_MODEL = "qwen2.5:1.5b"

# Embedding Model Configuration
DEFAULT_EMBEDDING_MODEL = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

EMBEDDING_BATCH_SIZE = 32

# Reranking Model Configuration
DEFAULT_RERANKER_MODEL = "ms-marco-MiniLM-L-12-v2"
MULTILINGUAL_RERANKER_MODEL = "ms-marco-MultiBERT-L-12"

# Storage Configuration
DATABASE_NAME = "learnsphere.db"

UPLOAD_DIRECTORY = "data/uploads"

GENERATED_DIRECTORY = "data/generated"

# Application Preferences
DEFAULT_THEME = "Light"

SUPPORTED_THEMES = [
    "Light",
    "Dark"
]

# ChromaDB Configuration
CHROMA_PERSIST_DIRECTORY = "document_store/chroma_db"
CHROMA_COLLECTION_NAME = "learnsphere_documents"
