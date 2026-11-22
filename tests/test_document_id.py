from modules.document_intelligence.document_manager import (
    process_and_store_document,
    remove_document
)
from services.vector_store import get_document_collection

def test_document_id(tmp_path):
    """Test document ID storage and deletion."""

    test_file = tmp_path / "document_id_test_temp.txt"

    test_file.write_text(
        "Artificial Intelligence helps computers perform intelligent tasks.",
        encoding="utf-8"
    )

    document_id = None

    try:
        # 1. Process and store the temporary document.
        result = process_and_store_document(test_file)

        document_id = result["document_id"]

        print("Document ID:", document_id)
        print("Source:", result["source"])
        print("Stored chunks:", result["total_chunks"])

        # 2. Verify ChromaDB stores the document ID.
        collection = get_document_collection()

        stored_data = collection.get(
            where={"document_id": document_id},
            include=["metadatas"]
        )

        assert len(stored_data["ids"]) > 0, (
            "Document ID was not found in ChromaDB."
        )

        print("Document ID storage verified!")

        # 3. Delete using the unique document ID.
        remove_document(document_id=document_id)
        document_id = None

        remaining_data = collection.get(
            where={"document_id": result["document_id"]},
            include=["metadatas"]
        )

        assert len(remaining_data["ids"]) == 0, (
            "Document chunks were not deleted."
        )

        print("Document deletion by ID verified!")
        print("\nDocument ID test passed!")

    finally:
        # Clean up if the test fails before deletion.
        if document_id is not None:
            remove_document(document_id=document_id)
