from pathlib import Path
from flashrank import Ranker, RerankRequest
from config.settings import (
    DEFAULT_RERANKER_MODEL,
    MULTILINGUAL_RERANKER_MODEL
)


# Store loaded models so they are not repeatedly downloaded or initialized.
_rankers = {}


# Keep model files inside the AI LearnSphere project.
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_CACHE_DIRECTORY = BASE_DIR / "model_cache"


def detect_query_language(query):
    """Detect Hindi or Punjabi written in their native scripts."""

    for character in query:
        code_point = ord(character)

        # Devanagari script (commonly used for Hindi).
        if 0x0900 <= code_point <= 0x097F:
            return "multilingual"

        # Gurmukhi script (commonly used for Punjabi).
        if 0x0A00 <= code_point <= 0x0A7F:
            return "multilingual"

    # Default to English for queries using the Latin alphabet.
    return "english"


def select_reranker_model(query):
    """Select a reranking model based on the query script."""

    language = detect_query_language(query)

    if language == "multilingual":
        return MULTILINGUAL_RERANKER_MODEL

    return DEFAULT_RERANKER_MODEL


def get_reranker(model_name=None):
    """Load a reranking model only when it is needed."""

    if model_name is None:
        model_name = DEFAULT_RERANKER_MODEL

    if model_name not in _rankers:
        MODEL_CACHE_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True
        )

        _rankers[model_name] = Ranker(
            model_name=model_name,
            cache_dir=str(MODEL_CACHE_DIRECTORY),
            max_length=512,
            log_level="WARNING"
        )

    return _rankers[model_name]


def rerank_documents(query, chunks, top_k=5):
    """Rerank retrieved document chunks by relevance to a query."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not chunks:
        return []

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    for chunk in chunks:
        if not isinstance(chunk, dict):
            raise ValueError("Every chunk must be a dictionary.")

        if not isinstance(chunk.get("text"), str) or not chunk["text"].strip():
            raise ValueError("Every chunk must contain non-empty text.")

    model_name = select_reranker_model(query)
    ranker = get_reranker(model_name)

    passages = [
        {
            "id": index,
            "text": chunk["text"],
            "meta": chunk.get("metadata", {})
        }
        for index, chunk in enumerate(chunks)
    ]

    request = RerankRequest(
        query=query,
        passages=passages
    )

    ranked_results = ranker.rerank(request)

    reranked_chunks = []

    for result in ranked_results:
        original_index = result["id"]

        original_chunk = chunks[original_index].copy()

        original_chunk["rerank_score"] = float(result["score"])
        original_chunk["reranker_model"] = model_name

        reranked_chunks.append(original_chunk)

    return reranked_chunks[:top_k]
