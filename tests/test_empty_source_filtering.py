from uuid import uuid4
from services.vector_store import (
    add_document_chunks,
    search_document_chunks,
    delete_document_chunks
)

def test_empty_source_filtering():
    """Verify that an empty source filter returns no results."""

    test_source = f"Empty_Filter_Test_{uuid4().hex}.txt"

    test_chunk = {
        "text": (
            "Artificial Intelligence enables machines "
            "to perform intelligent tasks."
        ),
        "metadata": {
            "source": test_source,
            "chunk": 0
        }
    }

    try:
        # 1. Add a temporary test document.
        add_document_chunks([test_chunk])

        # 2. Search with an empty source filter.
        results = search_document_chunks(
            query="Artificial Intelligence",
            top_k=5,
            sources=[]
        )

        print("Results with empty source list:", len(results))

        # 3. Verify expected behavior.
        assert results == [], (
            "Expected no results for an empty source list."
        )

        print("Empty-source filtering test passed!")

    finally:
        # 4. Remove only the temporary test document.
        delete_document_chunks(test_source)

        print("Temporary test document cleaned up.")
