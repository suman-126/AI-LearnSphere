import json
from database.db_manager import get_connection

def get_learning_history_preference():
    """Check whether the learner has enabled learning history."""

    with get_connection() as connection:
        learner = connection.execute(
            "SELECT save_learning_history FROM learner_profile ORDER BY id LIMIT 1"
        ).fetchone()

    if learner is None:
        return True

    return bool(learner["save_learning_history"])


def save_learner_profile(
    name=None,
    language="English",
    learning_level="Beginner",
    save_history=True
):
    """Save or update learner preferences."""

    with get_connection() as connection:
        learner = connection.execute(
            "SELECT id FROM learner_profile ORDER BY id LIMIT 1"
        ).fetchone()

        if learner:
            connection.execute("""
                UPDATE learner_profile
                SET name = ?,
                    preferred_language = ?,
                    learning_level = ?,
                    save_learning_history = ?
                WHERE id = ?
            """, (
                name,
                language,
                learning_level,
                int(save_history),
                learner["id"]
            ))
        else:
            connection.execute("""
                INSERT INTO learner_profile (
                    name,
                    preferred_language,
                    learning_level,
                    save_learning_history
                )
                VALUES (?, ?, ?, ?)
            """, (
                name,
                language,
                learning_level,
                int(save_history)
            ))


def save_quiz_result(
    subject,
    topic,
    difficulty,
    total_questions,
    correct_answers
):
    """Save a quiz result when learning history is enabled."""

    if not get_learning_history_preference():
        return False

    if total_questions <= 0:
        raise ValueError("Total questions must be greater than zero.")

    if not 0 <= correct_answers <= total_questions:
        raise ValueError("Correct answers must be within the question count.")

    percentage = (correct_answers / total_questions) * 100

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO quiz_results (
                subject,
                topic,
                difficulty,
                total_questions,
                correct_answers,
                score_percentage
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            subject,
            topic,
            difficulty,
            total_questions,
            correct_answers,
            percentage
        ))

    return True

def get_quiz_results():
    """Retrieve saved quiz results."""

    with get_connection() as connection:
        results = connection.execute("""
            SELECT * FROM quiz_results
            ORDER BY created_at DESC
        """).fetchall()

    return [dict(row) for row in results]


def save_topic_progress(subject, topic, status, progress_percentage):
    """Save or update progress for a learning topic."""

    progress_percentage = float(progress_percentage)

    if not 0 <= progress_percentage <= 100:
        raise ValueError("Progress must be between 0 and 100.")

    if not get_learning_history_preference():
        return False

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO topic_progress (
                subject,
                topic,
                status,
                progress_percentage,
                updated_at
            )
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(subject, topic)
            DO UPDATE SET
                status = excluded.status,
                progress_percentage = excluded.progress_percentage,
                updated_at = CURRENT_TIMESTAMP
        """, (
            subject,
            topic,
            status,
            progress_percentage
        ))

    return True


def get_topic_progress():
    """Retrieve saved topic progress."""

    with get_connection() as connection:
        results = connection.execute("""
            SELECT * FROM topic_progress
            ORDER BY updated_at DESC
        """).fetchall()

    return [dict(row) for row in results]

def register_document(
    document_id,
    filename,
    file_type,
    stored_path,
    total_chunks
):
    """Register an uploaded document in the database."""

    if not document_id or not filename or not stored_path:
        raise ValueError("Document ID, filename, and stored path are required.")

    if total_chunks <= 0:
        raise ValueError("Total chunks must be greater than zero.")

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO documents (
                document_id,
                filename,
                file_type,
                stored_path,
                total_chunks
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            document_id,
            filename,
            file_type,
            stored_path,
            total_chunks
        ))

    return True


def get_registered_documents():
    """Retrieve all registered documents."""

    with get_connection() as connection:
        results = connection.execute("""
            SELECT * FROM documents
            ORDER BY uploaded_at DESC
        """).fetchall()

    return [dict(row) for row in results]


def delete_registered_document(document_id):
    """Delete a document's database registry entry."""

    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM documents WHERE document_id = ?",
            (document_id,)
        )

    return cursor.rowcount > 0

def clear_learning_history():
    """Delete saved learning history and progress."""

    with get_connection() as connection:
        connection.execute("DELETE FROM learning_history")
        connection.execute("DELETE FROM quiz_results")
        connection.execute("DELETE FROM topic_progress")


def save_learning_history(session_title, subject, topic, data):
    """Save a learning session when history is enabled."""

    if not get_learning_history_preference():
        return False

    with get_connection() as connection:
        connection.execute("""
            INSERT INTO learning_history (
                session_title,
                subject,
                topic,
                conversation_data
            )
            VALUES (?, ?, ?, ?)
        """, (
            session_title,
            subject,
            topic,
            json.dumps(data, ensure_ascii=False)
        ))

    return True


def get_learning_history():
    """Retrieve saved learning history."""

    with get_connection() as connection:
        results = connection.execute("""
            SELECT * FROM learning_history
            ORDER BY created_at DESC
        """).fetchall()

    return [
        {
            **dict(row),
            "conversation_data": json.loads(row["conversation_data"])
            if row["conversation_data"] else {}
        }
        for row in results
    ]

