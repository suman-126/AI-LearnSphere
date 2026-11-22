from uuid import uuid4
from services.storage_manager import (
    register_document,
    get_registered_documents,
    delete_registered_document
)

def test_document_registry():
    """Test document registration, retrieval, and deletion."""

    test_document_id = f"test-document-{uuid4().hex}"

    try:
        # 1. Register a temporary document.
        register_document(
            document_id=test_document_id,
            filename="test_document.txt",
            file_type="txt",
            stored_path="temporary_test_document.txt",
            total_chunks=1
        )

        print("Document registration successful!")

        # 2. Verify that the document can be retrieved.
        documents = get_registered_documents()

        matching_documents = [
            document for document in documents
            if document["document_id"] == test_document_id
        ]

        assert len(matching_documents) == 1
        print("Document retrieval successful!")

        # 3. Verify stored information.
        print("Stored document:", matching_documents[0])

        # 4. Delete the temporary record.
        deleted = delete_registered_document(test_document_id)

        assert deleted is True
        print("Document deletion successful!")

        # 5. Confirm deletion.
        documents = get_registered_documents()

        assert not any(
            document["document_id"] == test_document_id
            for document in documents
        )

        print("Document registry test passed!")

    finally:
        # Clean up if the test fails before deletion.
        delete_registered_document(test_document_id)
