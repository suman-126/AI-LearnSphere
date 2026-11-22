from pathlib import Path

import pymupdf
from docx import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


SUPPORTED_FORMATS = {".pdf", ".txt", ".docx"}


def extract_document(file_path):
    """Extract text and metadata from PDF, TXT, or DOCX files."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    file_type = path.suffix.lower()

    if file_type not in SUPPORTED_FORMATS:
        raise ValueError(
            "Unsupported file format. Please use PDF, TXT, or DOCX."
        )

    extracted_documents = []

    if file_type == ".pdf":

        with pymupdf.open(path) as pdf:

            for page_number, page in enumerate(pdf, start=1):

                text = page.get_text("text").strip()

                if text:
                    extracted_documents.append({
                        "text": text,
                        "metadata": {
                            "source": path.name,
                            "page": page_number,
                            "file_type": "pdf"
                        }
                    })

    elif file_type == ".txt":

        try:
            text = path.read_text(encoding="utf-8")

        except UnicodeDecodeError:
            text = path.read_text(encoding="cp1252")

        text = text.strip()

        if text:
            extracted_documents.append({
                "text": text,
                "metadata": {
                    "source": path.name,
                    "page": None,
                    "file_type": "txt"
                }
            })

    elif file_type == ".docx":

        document = Document(path)
        current_section = "General"

        for paragraph in document.paragraphs:

            # Preserve leading spaces because they can be
            # important for Python code indentation.
            raw_text = paragraph.text

            if not raw_text.strip():
                continue

            heading_text = raw_text.strip()

            if paragraph.style.name.startswith("Heading"):
                current_section = heading_text

            extracted_documents.append({
                "text": raw_text.rstrip(),
                "metadata": {
                    "source": path.name,
                    "page": None,
                    "section": current_section,
                    "file_type": "docx"
                }
            })

    if not extracted_documents:
        raise ValueError(
            "No readable text was found in this document. "
            "It may be empty or contain scanned images only."
        )

    return extracted_documents


def chunk_document(
    extracted_documents,
    chunk_size=800,
    chunk_overlap=120
):
    """Split extracted documents while preserving their original order."""

    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if chunk_overlap < 0 or chunk_overlap >= chunk_size:
        raise ValueError("Invalid chunk overlap.")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = []
    chunk_counters = {}
    document_chunk_index = 0

    for document in extracted_documents:

        metadata = document["metadata"]

        counter_key = (
            metadata.get("source"),
            metadata.get("page"),
            metadata.get("section")
        )

        split_texts = splitter.split_text(document["text"])

        for chunk_text in split_texts:

            chunk_counters[counter_key] = (
                chunk_counters.get(counter_key, 0) + 1
            )

            document_chunk_index += 1

            chunks.append({
                "text": chunk_text,
                "metadata": {
                    **metadata,
                    "chunk": chunk_counters[counter_key],
                    "chunk_index": document_chunk_index
                }
            })

    return chunks


def process_document(file_path):
    """Extract and chunk a document in one operation."""

    extracted_documents = extract_document(file_path)

    chunks = chunk_document(extracted_documents)

    return chunks
