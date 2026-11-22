from fastembed import TextEmbedding

from config.settings import (
    DEFAULT_EMBEDDING_MODEL,
    EMBEDDING_BATCH_SIZE
)


_embedding_model = None


def get_embedding_model():
    """Load the embedding model only when needed."""

    global _embedding_model

    if _embedding_model is None:
        _embedding_model = TextEmbedding(
            model_name=DEFAULT_EMBEDDING_MODEL
        )

    return _embedding_model


def generate_embeddings(texts):
    """Generate numerical embeddings for a list of texts."""

    if isinstance(texts, str):
        texts = [texts]

    if not texts:
        return []

    if not all(isinstance(text, str) and text.strip() for text in texts):
        raise ValueError("All input texts must be non-empty strings.")

    model = get_embedding_model()

    embeddings = model.embed(
        texts,
        batch_size=EMBEDDING_BATCH_SIZE
    )

    return [embedding.tolist() for embedding in embeddings]


def generate_single_embedding(text):
    """Generate an embedding for one text."""

    return generate_embeddings([text])[0]


def get_embedding_dimension():
    """Return the number of values in an embedding vector."""

    sample_embedding = generate_single_embedding(
        "AI LearnSphere embedding test"
    )

    return len(sample_embedding)
