from pathlib import Path
from modules.document_intelligence.document_manager import (
    upload_document,
    remove_document
)
from services.storage_manager import get_registered_documents
from services.vector_store import get_document_collection

class TestUploadedFile:
    """Simulate a Streamlit uploaded file."""

    name = "learnsphere_upload_test.txt"

    def getvalue(self):
        return (
            b"Artificial Intelligence helps computers perform "
            b"intelligent tasks. Machine learning enables computers "
            b"to learn from data."
        )


def test_document_upload_lifecycle():
    """Test document upload, storage, registration, and deletion."""

    document_id = None
    stored_path = None

    try:
        # 1. Upload the test document.
        result = upload_document(TestUploadedFile())

        document_id = result["document_id"]
        stored_path = Path(result["stored_path"])

        assert document_id
        print("Document upload successful!")

        # 2. Verify ChromaDB storage.
        collection = get_document_collection()

        stored_chunks = collection.get(
            where={"document_id": document_id},
            include=["metadatas"]
        )

        assert len(stored_chunks["ids"]) > 0
        print("ChromaDB storage verified!")

        # 3. Verify physical file.
        assert stored_path.exists()
        print("Physical file storage verified!")

        # 4. Verify SQLite registration.
        documents = get_registered_documents()

        assert any(
            document["document_id"] == document_id
            for document in documents
        )

        print("SQLite registration verified!")

        # 5. Delete the document completely.
        remove_document(document_id=document_id)
        document_id = None

        print("Document deletion executed!")

        # 6. Verify ChromaDB deletion.
        remaining_chunks = collection.get(
            where={"document_id": result["document_id"]},
            include=["metadatas"]
        )

        assert len(remaining_chunks["ids"]) == 0
        print("ChromaDB deletion verified!")

        # 7. Verify SQLite deletion.
        documents = get_registered_documents()

        assert not any(
            document["document_id"] == result["document_id"]
            for document in documents
        )

        print("SQLite deletion verified!")

        # 8. Verify physical file deletion.
        assert not stored_path.exists()
        print("Physical file deletion verified!")

        print("Complete document lifecycle test passed!")

    finally:
        # Clean up if the test fails before deletion.
        if document_id is not None:
            remove_document(document_id=document_id)