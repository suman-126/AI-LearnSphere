import re
from rank_bm25 import BM25Okapi
from services.vector_store import search_document_chunks
from services.reranking_service import rerank_documents

def tokenize_text(text):
    """Convert text into lowercase tokens."""

    return re.findall(r"\w+", text.lower(), flags=re.UNICODE)

def semantic_search(query, chunks, top_k=5):
    """Find relevant chunks using persistent ChromaDB vectors."""

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not chunks:
        return []

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    # Prefer unique document IDs when all chunks have them.
    document_ids = list({
        chunk.get("metadata", {}).get("document_id")
        for chunk in chunks
        if chunk.get("metadata", {}).get("document_id")
    })

    if all(
        chunk.get("metadata", {}).get("document_id")
        for chunk in chunks
    ):
        stored_results = search_document_chunks(
            query=query,
            top_k=top_k,
            document_ids=document_ids
        )

    else:
        # Fall back to source names for older chunks.
        sources = list({
            chunk.get("metadata", {}).get("source")
            for chunk in chunks
            if chunk.get("metadata", {}).get("source")
        })

        stored_results = search_document_chunks(
            query=query,
            top_k=top_k,
            sources=sources
        )

    # Match results to the supplied original chunks.
    available_chunks = {
        ( 
            chunk.get("metadata", {}).get("document_id") or chunk.get("metadata", {}).get("source"),
            chunk.get("metadata", {}).get("source"),
            chunk.get("metadata", {}).get("page"),
            chunk.get("metadata", {}).get("section"),
            chunk.get("metadata", {}).get("chunk"),
            chunk["text"]
        ): chunk
        for chunk in chunks
    }

    scored_chunks = []

    for stored_chunk in stored_results:
        key = ( 
            stored_chunk.get("metadata", {}).get("document_id") or stored_chunk.get("metadata", {}).get("source"),
            stored_chunk.get("metadata", {}).get("source"),
            stored_chunk.get("metadata", {}).get("page"),
            stored_chunk.get("metadata", {}).get("section"),
            stored_chunk.get("metadata", {}).get("chunk"),
            stored_chunk["text"]
        )

        original_chunk = available_chunks.get(key)

        if original_chunk is None:
            continue

        result = original_chunk.copy()
        result["score"] = float(1.0 - stored_chunk["distance"])

        scored_chunks.append(result)

    return scored_chunks

def keyword_search(query, chunks, top_k=5):
    """Find relevant chunks using BM25 keyword ranking."""

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not chunks:
        return []

    if top_k <= 0:
        raise ValueError("top_k must be greater than zero.")

    tokenized_corpus = [
        tokenize_text(chunk["text"])
        for chunk in chunks
    ]

    tokenized_query = tokenize_text(query)

    if not tokenized_query:
        return []

    bm25 = BM25Okapi(tokenized_corpus)
    scores = bm25.get_scores(tokenized_query)

    scored_chunks = []

    for chunk, score in zip(chunks, scores):
        result = chunk.copy()
        result["score"] = float(score)

        scored_chunks.append(result)

    return sorted(
        scored_chunks,
        key=lambda item: item["score"],
        reverse=True
    )[:top_k]


def hybrid_search(query, chunks, top_k=5, candidate_k=10):
    """Combine semantic and keyword retrieval using RRF."""

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not chunks:
        return []

    if top_k <= 0 or candidate_k <= 0:
        raise ValueError("Retrieval limits must be greater than zero.")

    semantic_results = semantic_search(
        query,
        chunks,
        top_k=min(candidate_k, len(chunks))
    )

    keyword_results = keyword_search(
        query,
        chunks,
        top_k=min(candidate_k, len(chunks))
    )

    rrf_scores = {}
    chunk_lookup = {}

    def get_chunk_key(chunk):
        metadata = chunk.get("metadata", {})
        return (
            metadata.get("document_id") or metadata.get("source"),
            metadata.get("source"),
            metadata.get("page"),
            metadata.get("section"),
            metadata.get("chunk"),
            chunk["text"]
        )
    
    for results in (semantic_results, keyword_results):
        for rank, result in enumerate(results, start=1):
            key = get_chunk_key(result)

            rrf_scores[key] = rrf_scores.get(key, 0.0) + (
                1 / (60 + rank)
            )

            chunk_lookup[key] = result

    ranked_results = []

    for key, score in rrf_scores.items():
        result = chunk_lookup[key].copy()
        result["score"] = score
        ranked_results.append(result)

    ranked_results.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return ranked_results[:top_k]


def hybrid_search_with_reranking(
    query,
    chunks,
    top_k=5,
    candidate_k=10
):
    """Combine hybrid retrieval and reranking."""

    if not query or not query.strip():
        raise ValueError("Search query cannot be empty.")

    if not chunks:
        return []

    if top_k <= 0 or candidate_k <= 0:
        raise ValueError("Retrieval limits must be greater than zero.")

    # Retrieve a larger candidate set before reranking.
    candidate_results = hybrid_search(
        query=query,
        chunks=chunks,
        top_k=min(candidate_k, len(chunks)),
        candidate_k=candidate_k
    )

    if not candidate_results:
        return []

    # Rerank the retrieved candidates.
    final_results = rerank_documents(
        query=query,
        chunks=candidate_results,
        top_k=top_k
    )

    return final_results 
