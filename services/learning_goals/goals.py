from datetime import date, datetime
from database.db_manager import get_connection

VALID_GOAL_TYPES = {
    "Score Goal",
    "Practice Goal",
    "Topic Completion Goal"
}


def create_goal(
    goal_type,
    title,
    target_value,
    deadline,
    subject=None,
    topic=None
):
    """Create and save a new learning goal."""

    if goal_type not in VALID_GOAL_TYPES:
        raise ValueError("Invalid learning goal type.")

    if not title or not title.strip():
        raise ValueError("Goal title is required.")

    try:
        target_value = float(target_value)
    except (TypeError, ValueError):
        raise ValueError("Target value must be a number.")

    if target_value <= 0:
        raise ValueError("Target value must be greater than zero.")

    if goal_type in {"Score Goal", "Topic Completion Goal"}:
        if target_value > 100:
            raise ValueError("Percentage targets cannot exceed 100.")

    if goal_type == "Practice Goal":
        if not target_value.is_integer():
            raise ValueError("Practice session target must be a whole number.")

    try:
        deadline_date = date.fromisoformat(str(deadline))
    except (TypeError, ValueError):
        raise ValueError("Deadline must be a valid date.")

    if deadline_date < date.today():
        raise ValueError("Deadline cannot be in the past.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO learning_goals (
                goal_type,
                title,
                subject,
                topic,
                target_value,
                deadline,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, 'Active')
            """,
            (
                goal_type,
                title.strip(),
                subject.strip() if subject else None,
                topic.strip() if topic else None,
                target_value,
                deadline_date.isoformat()
            )
        )

        return cursor.lastrowid


def get_all_goals():
    """Retrieve all saved learning goals."""

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM learning_goals
            ORDER BY created_at DESC
            """
        ).fetchall()

        return [dict(row) for row in rows]


def get_goal_by_id(goal_id):
    """Retrieve a specific goal."""

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT *
            FROM learning_goals
            WHERE id = ?
            """,
            (goal_id,)
        ).fetchone()

        return dict(row) if row else None


def update_goal(goal_id, **updates):
    """Update editable learning goal fields."""

    allowed_fields = {
        "title",
        "subject",
        "topic",
        "target_value",
        "deadline"
    }

    if not updates:
        return False

    if not set(updates).issubset(allowed_fields):
        raise ValueError("Invalid goal field.")

    goal = get_goal_by_id(goal_id)

    if not goal:
        return False

    if "title" in updates:
        if not isinstance(updates["title"], str) or not updates["title"].strip():
            raise ValueError("Goal title is required.")
        updates["title"] = updates["title"].strip()

    if "target_value" in updates:
        try:
            value = float(updates["target_value"])
        except (TypeError, ValueError):
            raise ValueError("Target value must be a number.")

        if value <= 0:
            raise ValueError("Target value must be greater than zero.")

        if goal["goal_type"] in {"Score Goal", "Topic Completion Goal"} and value > 100:
            raise ValueError("Percentage targets cannot exceed 100.")

        if goal["goal_type"] == "Practice Goal" and not value.is_integer():
            raise ValueError("Practice session target must be a whole number.")

        updates["target_value"] = value

    if "deadline" in updates:
        try:
            updates["deadline"] = date.fromisoformat(
                str(updates["deadline"])
            ).isoformat()
        except (TypeError, ValueError):
            raise ValueError("Deadline must be a valid date.")

    for field in ("subject", "topic"):
        if field in updates and updates[field] is not None:
            updates[field] = updates[field].strip()

    set_clause = ", ".join(
        f"{field} = ?" for field in updates
    )

    values = list(updates.values())
    values.extend([datetime.now().isoformat(), goal_id])

    with get_connection() as connection:
        connection.execute(
            f"""
            UPDATE learning_goals
            SET {set_clause},
                updated_at = ?
            WHERE id = ?
            """,
            values
        )

    return True


def update_goal_status(goal_id, status):
    """Update a goal's status."""

    if status not in {"Active", "Completed", "Overdue"}:
        raise ValueError("Invalid goal status.")

    with get_connection() as connection:
        cursor = connection.execute(
            """
            UPDATE learning_goals
            SET status = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (status, datetime.now().isoformat(), goal_id)
        )

        return cursor.rowcount > 0


def delete_goal(goal_id):
    """Delete a learning goal."""

    with get_connection() as connection:
        cursor = connection.execute(
            """
            DELETE FROM learning_goals
            WHERE id = ?
            """,
            (goal_id,)
        )

        return cursor.rowcount > 0
