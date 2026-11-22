from datetime import date
from services.learning_goals.goals import (
    get_all_goals,
    get_goal_by_id,
    update_goal_status
)

from services.storage_manager import (
    get_quiz_results,
    get_learning_history,
    get_topic_progress
)


def _matches_goal(record, goal):
    """Check whether a learning record matches goal filters."""

    goal_subject = (goal.get("subject") or "").strip().lower()
    goal_topic = (goal.get("topic") or "").strip().lower()

    record_subject = (record.get("subject") or "").strip().lower()
    record_topic = (record.get("topic") or "").strip().lower()

    if goal_subject and record_subject != goal_subject:
        return False

    if goal_topic and record_topic != goal_topic:
        return False

    return True


def _get_score_progress(goal):
    """Find the highest matching Smart Quiz or MCQ score."""

    scores = []

    # Smart Quiz results
    for record in get_quiz_results():

        if not _matches_goal(record, goal):
            continue

        score = record.get("score_percentage")

        if score is not None:
            scores.append(float(score))

    # Practice Arena MCQ results
    for record in get_learning_history():

        if record.get("session_title") != "Practice Arena - MCQ":
            continue

        if not _matches_goal(record, goal):
            continue

        data = record.get("conversation_data") or {}
        summary = data.get("summary") or {}

        score = summary.get("percentage")

        if score is not None:
            scores.append(float(score))

    return max(scores, default=0.0)


def _get_practice_progress(goal):
    """Count matching completed Practice Arena MCQ sessions."""

    completed_sessions = 0

    for record in get_learning_history():

        if record.get("session_title") != "Practice Arena - MCQ":
            continue

        if not _matches_goal(record, goal):
            continue

        completed_sessions += 1

    return completed_sessions


def _get_topic_completion_progress(goal):
    """Retrieve progress for the matching learning topic."""

    subject = (goal.get("subject") or "").strip().lower()
    topic = (goal.get("topic") or "").strip().lower()

    if not subject or not topic:
        return 0.0

    for record in get_topic_progress():

        record_subject = (record.get("subject") or "").strip().lower()
        record_topic = (record.get("topic") or "").strip().lower()

        if record_subject == subject and record_topic == topic:
            return float(record.get("progress_percentage") or 0)

    return 0.0


def calculate_goal_progress(goal):
    """Calculate current progress and status for one learning goal."""

    goal_type = goal["goal_type"]
    target = float(goal["target_value"])

    if goal_type == "Score Goal":
        current = _get_score_progress(goal)

    elif goal_type == "Practice Goal":
        current = _get_practice_progress(goal)

    elif goal_type == "Topic Completion Goal":
        current = _get_topic_completion_progress(goal)

    else:
        raise ValueError("Unsupported learning goal type.")

    completion_percentage = min(
        (current / target) * 100,
        100
    )

    remaining = max(target - current, 0)

    is_completed = current >= target

    deadline = date.fromisoformat(str(goal["deadline"])[:10])

    if is_completed:
        status = "Completed"

    elif deadline < date.today():
        status = "Overdue"

    else:
        status = "Active"

    # Keep the database status synchronized with calculated status.
    if goal["status"] != status:
        update_goal_status(goal["id"], status)

    return {
        "id": goal["id"],
        "title": goal["title"],
        "goal_type": goal_type,
        "subject": goal.get("subject"),
        "topic": goal.get("topic"),
        "current_value": current,
        "target_value": target,
        "remaining": remaining,
        "completion_percentage": round(completion_percentage, 2),
        "deadline": str(goal["deadline"]),
        "status": status
    }


def get_goal_progress(goal_id):
    """Get calculated progress for one saved goal."""

    goal = get_goal_by_id(goal_id)

    if not goal:
        return None

    return calculate_goal_progress(goal)


def get_all_goal_progress():
    """Get calculated progress for every saved learning goal."""

    goals = get_all_goals()

    return [
        calculate_goal_progress(goal)
        for goal in goals
    ]
