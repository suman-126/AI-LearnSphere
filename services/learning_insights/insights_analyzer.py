from services.storage_manager import (
    get_quiz_results,
    get_learning_history
)


def _safe_number(value, default=0):
    """Convert a value to a number safely."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _create_session(
    source,
    subject,
    topic,
    difficulty,
    total_questions,
    correct_answers,
    created_at
):
    """Create a standardized learning session record."""

    total_questions = int(_safe_number(total_questions))
    correct_answers = int(_safe_number(correct_answers))

    if total_questions <= 0:
        return None

    if not 0 <= correct_answers <= total_questions:
        return None

    score = (correct_answers / total_questions) * 100

    return {
        "source": source,
        "subject": subject or "Unspecified",
        "topic": topic or "Unspecified",
        "difficulty": difficulty or "Not specified",
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "incorrect_answers": total_questions - correct_answers,
        "score_percentage": round(score, 2),
        "created_at": created_at
    }


def get_learning_sessions():
    """
    Collect Smart Quiz and Practice Arena MCQ results
    in a standardized format.
    """

    sessions = []

    # Collect Smart Quiz results
    for record in get_quiz_results():

        session = _create_session(
            source="Smart Quiz",
            subject=record.get("subject"),
            topic=record.get("topic"),
            difficulty=record.get("difficulty"),
            total_questions=record.get("total_questions"),
            correct_answers=record.get("correct_answers"),
            created_at=record.get("created_at")
        )

        if session:
            sessions.append(session)

    # Collect Practice Arena MCQ results
    for record in get_learning_history():

        if record.get("session_title") != "Practice Arena - MCQ":
            continue

        data = record.get("conversation_data") or {}
        summary = data.get("summary") or {}

        session = _create_session(
            source="Practice Arena",
            subject=record.get("subject"),
            topic=record.get("topic"),
            difficulty=data.get("difficulty"),
            total_questions=summary.get("total_questions"),
            correct_answers=summary.get("correct_answers"),
            created_at=record.get("created_at")
        )

        if session:
            sessions.append(session)

    # Sort all sessions by date, newest first.
    sessions.sort(
        key=lambda item: item.get("created_at") or "",
        reverse=True
    )

    return sessions


def _calculate_group_performance(sessions, group_field):
    """Calculate performance grouped by subject or topic."""

    groups = {}

    for session in sessions:

        if group_field == "topic":
            key = (
                session["subject"],
                session["topic"]
            )
        else:
            key = session[group_field]

        if key not in groups:
            groups[key] = {
                "attempts": 0,
                "total_questions": 0,
                "correct_answers": 0
            }

        groups[key]["attempts"] += 1
        groups[key]["total_questions"] += session["total_questions"]
        groups[key]["correct_answers"] += session["correct_answers"]

    performance = []

    for key, values in groups.items():

        total_questions = values["total_questions"]
        correct_answers = values["correct_answers"]

        average_score = (
            correct_answers / total_questions
        ) * 100 if total_questions else 0

        if group_field == "topic":
            subject, topic = key
            result = {
                "subject": subject,
                "topic": topic
            }
        else:
            result = {
                "subject": key
            }

        result.update({
            "attempts": values["attempts"],
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "average_score": round(average_score, 2)
        })

        performance.append(result)

    performance.sort(
        key=lambda item: item["average_score"],
        reverse=True
    )

    return performance


def get_performance_analysis():
    """
    Generate combined performance analysis
    from Smart Quiz and Practice Arena.
    """

    sessions = get_learning_sessions()

    total_sessions = len(sessions)

    total_questions = sum(
        session["total_questions"]
        for session in sessions
    )

    correct_answers = sum(
        session["correct_answers"]
        for session in sessions
    )

    incorrect_answers = total_questions - correct_answers

    overall_accuracy = (
        correct_answers / total_questions
    ) * 100 if total_questions else 0

    average_session_score = (
        sum(
            session["score_percentage"]
            for session in sessions
        ) / total_sessions
    ) if total_sessions else 0

    quiz_sessions = sum(
        session["source"] == "Smart Quiz"
        for session in sessions
    )

    practice_sessions = sum(
        session["source"] == "Practice Arena"
        for session in sessions
    )

    return {
        "overall": {
            "total_sessions": total_sessions,
            "quiz_sessions": quiz_sessions,
            "practice_sessions": practice_sessions,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "incorrect_answers": incorrect_answers,
            "overall_accuracy": round(overall_accuracy, 2),
            "average_session_score": round(
                average_session_score, 2
            )
        },
        "subject_performance": _calculate_group_performance(
            sessions,
            "subject"
        ),
        "topic_performance": _calculate_group_performance(
            sessions,
            "topic"
        ),
        "sessions": sessions
    }
