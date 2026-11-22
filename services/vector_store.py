import hashlib
from services.embedding_service import generate_embeddings
from pathlib import Path
import chromadb

from config.settings import (
    CHROMA_PERSIST_DIRECTORY,
    CHROMA_COLLECTION_NAME
)

BASE_DIR = Path(__file__).resolve().parent.parent

PERSIST_DIRECTORY = BASE_DIR / CHROMA_PERSIST_DIRECTORY

_client = None
_collection = None


def get_chroma_client():
    """Create or return the persistent ChromaDB client."""
    global _client

    if _client is None:
        PERSIST_DIRECTORY.mkdir(parents=True, exist_ok=True)

        _client = chromadb.PersistentClient(
            path=str(PERSIST_DIRECTORY)
        )

    return _client


def get_document_collection():
    """Create or return the LearnSphere document collection."""
    global _collection

    if _collection is None:
        client = get_chroma_client()

        _collection = client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    return _collection


def get_collection_count():
    """Return the total number of stored document chunks."""
    collection = get_document_collection()
    return collection.count()

# storage function

def add_document_chunks(chunks):
    """Generate embeddings and store document chunks in ChromaDB."""

    if not chunks:
        return 0

    for chunk in chunks:
        if not isinstance(chunk, dict):
            raise ValueError("Every chunk must be a dictionary.")

        if not isinstance(chunk.get("text"), str) or not chunk["text"].strip():
            raise ValueError("Every chunk must contain non-empty text.")

    collection = get_document_collection()

    texts = [chunk["text"] for chunk in chunks]
    embeddings = generate_embeddings(texts)

    ids = []
    documents = []
    metadatas = []

    for chunk, text, embedding in zip(chunks, texts, embeddings):
        metadata = chunk.get("metadata", {})

        source = str(metadata.get("source", "unknown"))
        document_id = str(metadata.get("document_id", source))
        page = str(metadata.get("page", ""))
        section = str(metadata.get("section", ""))
        chunk_index = str(metadata.get("chunk", metadata.get("chunk_index", "")))

        unique_text = f"{document_id}|{page}|{section}|{chunk_index}|{text}"

        chunk_id = hashlib.sha256(
            unique_text.encode("utf-8")
        ).hexdigest()

        clean_metadata = {
            str(key): value
            for key, value in metadata.items()
            if isinstance(value, (str, int, float, bool))
        }

        clean_metadata["source"] = source
        clean_metadata["document_id"] = document_id

        ids.append(chunk_id)
        documents.append(text)
        metadatas.append(clean_metadata)

    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=documents,
        metadatas=metadatas
    )

    return len(ids)

# Semantic function

def search_document_chunks(query, top_k=5, sources=None, document_ids=None ):
    """Find the most relevant stored document chunks."""

    if not isinstance(query, str) or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    collection = get_document_collection()

    if collection.count() == 0:
        return []

    query_embedding = generate_embeddings([query])[0]

    if sources is not None and not sources:
       return []
    
    if document_ids is not None and not document_ids:
       return []

    query_arguments = {
        "query_embeddings": [query_embedding],
        "n_results": min(top_k, collection.count()),
        "include": ["documents", "metadatas", "distances"]
    }

    filters = []

    if sources is not None:
       filters.append({"source": {"$in": sources}})

    if document_ids is not None:
       filters.append({"document_id": {"$in": document_ids}})

    if len(filters) == 1:
       query_arguments["where"] = filters[0]

    elif len(filters) > 1:
       query_arguments["where"] = {"$and": filters}

    results = collection.query(**query_arguments)
    matched_chunks = []

    for index in range(len(results["ids"][0])):
        matched_chunks.append({
            "text": results["documents"][0][index],
            "metadata": results["metadatas"][0][index],
            "distance": results["distances"][0][index]
        })

    return matched_chunks

# document deletion

def delete_document_chunks(source=None, document_id=None):
    """Delete document chunks using a unique ID or source name."""

    if document_id is not None:
        if not isinstance(document_id, str) or not document_id.strip():
            raise ValueError("Document ID cannot be empty.")

        delete_filter = {"document_id": document_id}

    elif source is not None:
        if not isinstance(source, str) or not source.strip():
            raise ValueError("Document source cannot be empty.")

        delete_filter = {"source": source}

    else:
        raise ValueError("Provide a document source or document ID.")

    collection = get_document_collection()

    collection.delete(where=delete_filter)

    return True
    