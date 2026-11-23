from .document_qa_graph import (
    _is_python_statement,
    extract_python_code,
    _get_chunk_order,
    _expand_neighboring_chunks,
    _is_code_question,
    _build_source_record,
    run_document_qa_graph
)

def answer_document_question(
    query,
    document_ids,
    model=None,
    top_k=5,
    candidate_k=10
):
    """
    Answer questions using the LangGraph document-QA workflow.

    Keeps the original function signature and result structure
    so the existing Streamlit interface remains compatible.
    """

    return run_document_qa_graph(
        query=query,
        document_ids=document_ids,
        model=model,
        top_k=top_k,
        candidate_k=candidate_k
    )


if __name__ == "__main__":

    sample = '''Example:
def greet():
    print("Hello, World!")'''

    print(extract_python_code(sample))