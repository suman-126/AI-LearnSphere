from pathlib import Path
from modules.document_intelligence.document_manager import (
    upload_document,
    remove_document
)
from modules.document_intelligence.document_qa import (
    answer_document_question
)

def test_document_qa():
    """Test document upload and question answering."""

    sample_path = Path(__file__).parent / "sample_learning_document.txt"

    assert sample_path.exists(), "Sample learning document not found."

    class TestUploadedFile:
        name = sample_path.name

        def getvalue(self):
            return sample_path.read_bytes()

    document_id = None

    try:
        # Upload the sample document.
        result = upload_document(TestUploadedFile())

        document_id = result["document_id"]

        print("Document uploaded successfully!")
        print("Document ID:", document_id)
        print("Stored chunks:", result["total_chunks"])

        # Ask a question about the uploaded document.
        qa_result = answer_document_question(
            query="What is a variable in Python, and how is it created?",
            document_ids=[document_id]
        )

        print("\nAI Answer:")
        print(qa_result["answer"])

        print("\nSource References:")
        for source in qa_result["sources"]:
            print(source)

        print("\nRetrieved Chunks:", qa_result["retrieval_count"])

        # Verify the Q&A result.
        assert qa_result["answer"]
        assert qa_result["retrieval_count"] > 0
        assert qa_result["sources"]

        print("\nDocument Q&A integration test passed!")

    finally:
        # Remove the temporary uploaded document.
        if document_id is not None:
            remove_document(document_id=document_id)
