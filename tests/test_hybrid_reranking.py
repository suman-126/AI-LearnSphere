from uuid import uuid4
from services.vector_store import (
    add_document_chunks,
    delete_document_chunks
)
from services.retrieval_service import hybrid_search_with_reranking

def test_hybrid_reranking():
    """Test hybrid retrieval followed by FlashRank reranking."""

    document_id = f"rerank-test-{uuid4().hex}"

    chunks = [
        {
            "text": "Python is a popular programming language.",
            "metadata": {
                "source": "Notes.txt",
                "document_id": document_id,
                "chunk": 0
            }
        },
        {
            "text": "Machine learning enables computers to learn from data.",
            "metadata": {
                "source": "Notes.txt",
                "document_id": document_id,
                "chunk": 1
            }
        },
        {
            "text": "Deep learning uses neural networks to solve complex problems.",
            "metadata": {
                "source": "Notes.txt",
                "document_id": document_id,
                "chunk": 2
            }
        }
    ]

    try:
        # Store temporary chunks for semantic retrieval.
        add_document_chunks(chunks)

        query = "How do computers learn from data?"

        results = hybrid_search_with_reranking(
            query=query,
            chunks=chunks,
            top_k=3,
            candidate_k=3
        )

        print("\nHybrid retrieval with reranking results:")

        for result in results:
            print(
                f"Rerank Score: {result['rerank_score']:.4f} | "
                f"RRF Score: {result['score']:.5f} | "
                f"Text: {result['text']}"
            )

        assert len(results) > 0, "No reranked results returned."

        assert all(
            "rerank_score" in result for result in results
        ), "Reranking scores are missing."

        assert all(
            "score" in result for result in results
        ), "RRF scores are missing."

        print("\nHybrid retrieval with reranking test passed!")

    finally:
        # Remove only this test's temporary ChromaDB chunks.
        delete_document_chunks(document_id=document_id)