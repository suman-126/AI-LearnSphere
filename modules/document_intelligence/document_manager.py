from pathlib import Path
import uuid

from config.settings import UPLOAD_DIRECTORY

from services.document_processor import (
    process_document as extract_and_chunk_document,
    SUPPORTED_FORMATS
)

from services.vector_store import (
    add_document_chunks,
    delete_document_chunks
)

from services.storage_manager import (
    register_document,
    get_registered_documents,
    delete_registered_document
)


# Project directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Permanent upload directory
UPLOAD_PATH = BASE_DIR / UPLOAD_DIRECTORY


def process_and_store_document(file_path, filename=None):
    """
    Process a document, store its chunks in ChromaDB,
    and register its details in SQLite.
    """

    path = Path(file_path)
    document_id = str(uuid.uuid4())

    if not path.exists():
        raise FileNotFoundError(f"Document not found: {path}")

    file_type = path.suffix.lower()

    if file_type not in SUPPORTED_FORMATS:
        raise ValueError(
            "Unsupported file format. Please use PDF, TXT, or DOCX."
        )

    stored_in_chroma = False

    try:
        # Extract text and divide it into chunks.
        chunks = extract_and_chunk_document(path)

        if not chunks:
            raise ValueError("No document chunks were generated.")

        # Attach the unique document ID to every chunk.
        for chunk in chunks:
            chunk.setdefault("metadata", {})["document_id"] = document_id

        # Store chunks and embeddings in ChromaDB.
        stored_count = add_document_chunks(chunks)
        stored_in_chroma = True

        if stored_count <= 0:
            raise ValueError("Document chunks could not be stored.")

        # Register document details in SQLite.
        register_document(
            document_id=document_id,
            filename=filename or path.name,
            file_type=file_type.lstrip("."),
            stored_path=str(path.resolve()),
            total_chunks=stored_count
        )

        return {
            "document_id": document_id,
            "source": filename or path.name,
            "stored_path": str(path.resolve()),
            "total_chunks": stored_count,
            "chunks": chunks
        }

    except Exception:
        # Remove any chunks stored for this document.
        if stored_in_chroma:
            try:
                delete_document_chunks(document_id=document_id)
            except Exception:
                pass

        raise


def upload_document(uploaded_file):
    """
    Save an uploaded file using a unique filename,
    process it, and register it.
    """

    if uploaded_file is None:
        raise ValueError("Please select a document.")

    original_filename = Path(uploaded_file.name).name
    file_type = Path(original_filename).suffix.lower()

    if file_type not in SUPPORTED_FORMATS:
        raise ValueError(
            "Unsupported file format. Please upload PDF, TXT, or DOCX."
        )

    UPLOAD_PATH.mkdir(parents=True, exist_ok=True)

    # Generate a unique physical filename.
    stored_filename = f"{uuid.uuid4().hex}{file_type}"
    stored_file_path = UPLOAD_PATH / stored_filename

    try:
        # Save the uploaded file.
        stored_file_path.write_bytes(uploaded_file.getvalue())

        if stored_file_path.stat().st_size == 0:
            raise ValueError("The uploaded document is empty.")

        # Process, store and register the document.
        return process_and_store_document(
            file_path=stored_file_path,
            filename=original_filename
        )

    except Exception:
        # Remove the physical file if processing or registration fails.
        stored_file_path.unlink(missing_ok=True)
        raise


def remove_document(source=None, document_id=None):
    """
    Completely remove a registered document from
    ChromaDB, SQLite and physical file storage.
    """

    documents = get_registered_documents()

    if document_id is not None:
        if not isinstance(document_id, str) or not document_id.strip():
            raise ValueError("Document ID cannot be empty.")

        matching_documents = [
            document for document in documents
            if document["document_id"] == document_id
        ]

        document_ids = [document_id]

    elif source is not None:
        if not isinstance(source, str) or not source.strip():
            raise ValueError("Document source cannot be empty.")

        matching_documents = [
            document for document in documents
            if document["filename"] == source
        ]

        document_ids = [
            document["document_id"]
            for document in matching_documents
        ]

        # Preserve compatibility with older, unregistered documents.
        if not document_ids:
            delete_document_chunks(source=source)
            return True

    else:
        raise ValueError(
            "Provide a document source or document ID."
        )

    for current_id in document_ids:

        matching_record = next(
            (
                document for document in matching_documents
                if document["document_id"] == current_id
            ),
            None
        )

        # Remove chunks from ChromaDB.
        delete_document_chunks(document_id=current_id)

        # Remove the SQLite registry entry.
        delete_registered_document(current_id)

        # Remove the physical file.
        if matching_record:
            stored_path = Path(matching_record["stored_path"])
            stored_path.unlink(missing_ok=True)

    return True
