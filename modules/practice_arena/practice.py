from modules.quiz_generator.quiz import (
    generate_quiz,
    evaluate_quiz,
    generate_quiz_result
)


def create_practice_session(
    subject,
    topic,
    difficulty="Beginner",
    num_questions=5,
    timed=False,
    time_limit_minutes=None
):
    """Create an MCQ practice session."""

    if not subject or not subject.strip():
        raise ValueError("Subject is required.")

    if not topic or not topic.strip():
        raise ValueError("Topic is required.")

    if num_questions not in [5, 10, 15, 20]:
        raise ValueError("Question count must be 5, 10, 15 or 20.")

    if difficulty not in ["Beginner", "Intermediate", "Advanced"]:
        raise ValueError("Invalid difficulty level.")

    if timed:
        if (
            not isinstance(time_limit_minutes, int)
            or isinstance(time_limit_minutes, bool)
            or time_limit_minutes <= 0
        ):
            raise ValueError("A valid time limit is required for timed practice.")

    quiz = generate_quiz(
        subject=subject.strip(),
        topic=topic.strip(),
        difficulty=difficulty,
        num_questions=num_questions
    )

    return {
        "subject": quiz["subject"],
        "topic": quiz["topic"],
        "difficulty": quiz["difficulty"],
        "questions": quiz["questions"],
        "total_questions": len(quiz["questions"]),
        "timed": timed,
        "time_limit_minutes": time_limit_minutes if timed else None
    }


def evaluate_practice_session(session, user_answers):
    """Evaluate submitted answers for a practice session."""

    if not isinstance(session, dict):
        raise ValueError("Invalid practice session.")

    if not isinstance(user_answers, dict):
        raise ValueError("Answers must be provided as a dictionary.")

    quiz = {
        "subject": session["subject"],
        "topic": session["topic"],
        "difficulty": session["difficulty"],
        "total_questions": session["total_questions"],
        "questions": session["questions"]
    }

    evaluation = evaluate_quiz(
        quiz=quiz,
        user_answers=user_answers
    )

    result = generate_quiz_result(evaluation)

    return {
        "subject": session["subject"],
        "topic": session["topic"],
        "difficulty": session["difficulty"],
        "timed": session["timed"],
        "time_limit_minutes": session["time_limit_minutes"],
        "summary": result["summary"],
        "performance": result["performance"],
        "message": result["message"],
        "detailed_results": result["detailed_results"]
    }
