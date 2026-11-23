# AI LearnSphere – Intelligent Learning & Skill Development Platform

AI LearnSphere is an AI-powered learning platform designed to make education more interactive, personalized, and effective. It provides an integrated environment where learners can explore academic subjects, understand concepts, evaluate their knowledge, practice skills, and track their learning progress.

The platform combines Generative AI, Retrieval-Augmented Generation (RAG), document intelligence, LangGraph workflow orchestration, and personalized learning features to support an engaging learning experience.

## Key Features

### 1. AI Tutor
- Ask questions across different academic subjects.
- Get AI-generated explanations and answers.
- Ask follow-up questions for better understanding.

### 2. Smart Quiz
- Generate subject- and topic-based quizzes.
- Practice questions at different difficulty levels.
- Evaluate answers and view quiz results.

### 3. Knowledge Evaluator
- Evaluate understanding of a selected topic.
- Identify knowledge gaps.
- Receive feedback to improve learning.

### 4. Document Intelligence
- Upload PDF, TXT, and DOCX documents.
- Extract and process document content.
- Ask questions about uploaded documents.
- Retrieve relevant information with source references.
- Use hybrid retrieval and reranking for document-based question answering.
- Use LangGraph to orchestrate the document question-answering workflow.

### 5. Practice Arena
- Practice multiple-choice questions.
- Attempt timed practice sessions.
- Review answers and performance.

### 6. Coding Challenges
- Explore programming challenges.
- Practice Python coding concepts.
- Receive AI-assisted code evaluation and feedback.

### 7. Learning Roadmap
- Follow structured subject and topic learning paths.
- Track topic completion and progress.
- Organize learning goals.

### 8. My Learning Journey
- Monitor learning activities and progress.
- Review learning statistics.
- Track personal learning goals.

### 9. AI Learning Insights
- Analyze learning performance.
- Identify strengths and areas requiring improvement.
- Receive AI-generated learning suggestions.

### 10. Learning History
- Access previously saved learning sessions.
- Review past learning activities and results.

### 11. Settings
- Manage learner preferences.
- Configure language and learning level.
- Control learning history preferences.

## Technologies Used

| Category | Technologies |
|---|---|
| Programming Language | Python |
| User Interface | Streamlit |
| Workflow Orchestration | LangGraph |
| Data Processing | Pandas |
| Database | SQLite |
| Vector Database | ChromaDB |
| Embeddings | FastEmbed |
| Retrieval | Semantic Search, BM25 |
| Reranking | FlashRank |
| RAG | Retrieval-Augmented Generation |
| Document Processing | PyMuPDF, python-docx |
| AI Model Runtime | Ollama |
| Visualization | Plotly |
| Environment Configuration | python-dotenv |
| Testing | Pytest |

## AI and Retrieval Architecture

AI LearnSphere integrates multiple AI and information retrieval techniques:

- **Generative AI:** Provides interactive learning assistance and AI-generated educational content.
- **RAG:** Retrieves relevant document information to support context-aware question answering.
- **Semantic Search:** Finds relevant information based on meaning.
- **BM25 Keyword Search:** Retrieves information using keyword relevance.
- **Hybrid Retrieval:** Combines semantic and keyword-based retrieval.
- **Reciprocal Rank Fusion (RRF):** Combines rankings from multiple retrieval methods.
- **FlashRank Reranking:** Reorders retrieved results based on relevance.
- **LangGraph:** Orchestrates the Document Intelligence question-answering workflow using a structured graph with conditional routing.

### LangGraph Integration – Document Question Answering

LangGraph is integrated into the Document Intelligence module to manage the document question-answering workflow.

The workflow includes:

1. **Validation:** Validates the user's question, selected documents, and retrieval settings.
2. **Question Classification:** Identifies whether the question requires original code extraction or normal document-based retrieval.
3. **Conditional Routing:**
   - Code-related questions follow the code extraction path.
   - Normal questions follow the document retrieval path.
4. **Hybrid Retrieval and Reranking:** Retrieves relevant document chunks using the existing retrieval and reranking services.
5. **Context Preparation:** Prepares relevant information and source references.
6. **Answer Generation:** Uses the existing Ollama-based response generation service to generate a document-grounded answer.
7. **Result Return:** Returns the answer and source references to the Streamlit interface.

The integration uses LangGraph for workflow orchestration while preserving the existing document processing, retrieval, reranking, and answer-generation components.

### LangGraph Workflow Overview

```text
Streamlit Interface
        |
        v
Document QA Wrapper
(document_qa.py)
        |
        v
LangGraph Workflow
(document_qa_graph.py)
        |
        v
Validate Documents and Question
        |
        v
Classify Question
        |
        +-----------------------+
        |                       |
        v                       v
  Code Question          Normal Question
        |                       |
        v                       v
  Extract Original       Hybrid Retrieval
  Code Examples          and Reranking
        |                       |
        +-----------+-----------+
                    |
                    v
           Prepare Context
           and Source References
                    |
                    v
           Generate Answer
               (Ollama)
                    |
                    v
           Return Final Result
                    |
                    v
             Streamlit UI
```

## Project Structure

```text
AI_LearnSphere/
│
├── assets/
├── config/
├── data/
├── database/
├── document_store/
├── model_cache/
├── modules/
├── services/
├── tests/
├── utils/
│
├── .gitignore
├── README.md
├── requirements.txt
└── stream.py
```

## Installation and Setup

### Prerequisites

- Python 3.10 or later
- pip
- Git (optional, for cloning the repository)
- Ollama with a compatible local model for AI-powered features

### 1. Clone the Repository

```bash
git clone https://github.com/suman-126/AI-LearnSphere.git
```

### 2. Navigate to the Project Directory

```bash
cd AI_LearnSphere
```

### 3. Create a Virtual Environment

```bash
python -m venv myenv
```

### 4. Activate the Virtual Environment

**Windows PowerShell:**

```powershell
.\myenv\Scripts\Activate.ps1
```

### 5. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Run the Application

```bash
streamlit run stream.py
```

The application will open in your default web browser.

## Testing

The project includes automated tests using Pytest.

Run the complete test suite:

```bash
python -m pytest -v
```

The current automated test suite contains 10 tests, all of which passed during project verification.

## Future Scope

- Expand support for additional academic subjects and learning resources.
- Improve personalized learning recommendations.
- Enhance document understanding and retrieval capabilities.
- Introduce additional learning analytics and evaluation methods.
- Extend support for more programming languages and coding exercises.

## Author

**Suman**

Passionate about exploring Artificial Intelligence and building practical AI-powered applications. Interested in Generative AI, intelligent systems, and innovative learning technologies.