from uuid import uuid4
from services.vector_store import (
    add_document_chunks,
    search_document_chunks,
    delete_document_chunks
)

def test_document_id_filtering():
    """Verify retrieval results are filtered by document ID."""

    unique_id = uuid4().hex

    python_document_id = f"python-test-{unique_id}"
    ml_document_id = f"ml-test-{unique_id}"

    test_chunks = [
        {
            "text": "Python is a popular programming language.",
            "metadata": {
                "source": f"Python_Notes_{unique_id}.txt",
                "document_id": python_document_id,
                "chunk": 0
            }
        },
        {
            "text": "Machine learning uses data to learn patterns.",
            "metadata": {
                "source": f"ML_Notes_{unique_id}.txt",
                "document_id": ml_document_id,
                "chunk": 0
            }
        }
    ]

    try:
        # 1. Add temporary test documents.
        add_document_chunks(test_chunks)

        # 2. Search using only the Python document ID.
        results = search_document_chunks(
            query="programming language",
            top_k=5,
            document_ids=[python_document_id]
        )

        print("Document ID filtering results:")

        for result in results:
            print("Document ID:", result["metadata"]["document_id"])
            print("Source:", result["metadata"]["source"])
            print("Text:", result["text"])

        # 3. Verify matching results.
        assert len(results) > 0, "No matching document found."

        assert all(
            result["metadata"]["document_id"] == python_document_id
            for result in results
        ), "Unexpected document ID found!"

        print("\nDocument ID filtering test passed!")

    finally:
        # 4. Remove only the temporary test documents.
        delete_document_chunks(document_id=python_document_id)
        delete_document_chunks(document_id=ml_document_id)

        print("Temporary test documents cleaned up.")
