from uuid import uuid4
from services.vector_store import (
    add_document_chunks,
    search_document_chunks,
    delete_document_chunks
)

def test_source_filtering():
    """Verify retrieval results are filtered by source."""

    unique_id = uuid4().hex

    python_source = f"Python_Test_{unique_id}.txt"
    ml_source = f"ML_Test_{unique_id}.txt"

    test_chunks = [
        {
            "text": "Python is a programming language.",
            "metadata": {
                "source": python_source,
                "chunk": 0
            }
        },
        {
            "text": "Machine learning uses data to learn patterns.",
            "metadata": {
                "source": ml_source,
                "chunk": 0
            }
        }
    ]

    try:
        # 1. Add temporary test documents.
        add_document_chunks(test_chunks)

        # 2. Search using only the Python source.
        results = search_document_chunks(
            query="programming language",
            top_k=5,
            sources=[python_source]
        )

        print("Filtered search results:")

        for result in results:
            print("Source:", result["metadata"]["source"])
            print("Text:", result["text"])

        # 3. Verify that only the requested source is returned.
        assert len(results) > 0, "No matching source found."

        assert all(
            result["metadata"]["source"] == python_source
            for result in results
        ), "Unexpected document found!"

        print("\nSource filtering test passed!")

    finally:
        # 4. Remove only the temporary test documents.
        delete_document_chunks(python_source)
        delete_document_chunks(ml_source)

        print("Temporary test documents cleaned up.")
