from uuid import uuid4
from services.vector_store import (
    add_document_chunks,
    delete_document_chunks
)
from services.retrieval_service import semantic_search

def test_semantic_retrieval():
    """Test semantic retrieval using a natural-language query."""

    test_source = f"Semantic_Test_{uuid4().hex}.txt"

    test_chunks = [
        {
            "text": "Python is a popular programming language.",
            "metadata": {
                "source": test_source,
                "chunk": 0
            }
        },
        {
            "text": "Machine learning enables computers to learn from data.",
            "metadata": {
                "source": test_source,
                "chunk": 1
            }
        },
        {
            "text": "Deep learning uses neural networks.",
            "metadata": {
                "source": test_source,
                "chunk": 2
            }
        }
    ]

    try:
        # 1. Add temporary test chunks.
        add_document_chunks(test_chunks)

        # 2. Perform semantic retrieval.
        results = semantic_search(
            query="How do computers learn from data?",
            chunks=test_chunks,
            top_k=3
        )

        print("Semantic retrieval results:")

        for result in results:
            print(
                f"Chunk: {result['metadata']['chunk']} | "
                f"Score: {result['score']:.4f} | "
                f"Text: {result['text']}"
            )

        # 3. Verify retrieval results.
        assert len(results) > 0, "No semantic results returned."

        print("\nSemantic retrieval test passed!")

    finally:
        # 4. Remove temporary test chunks.
        delete_document_chunks(test_source)

        print("Temporary test document cleaned up.")
