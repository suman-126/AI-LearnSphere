from services.learning_insights.insights_analyzer import (
    get_learning_sessions
)

def analyze_learning_trends():
    """
    Compare recent learning performance with earlier performance.

    Uses the five most recent sessions and the five sessions
    immediately before them.
    """

    sessions = get_learning_sessions()

    total_sessions = len(sessions)

    if total_sessions < 2:
        return {
            "status": "Insufficient Data",
            "message": (
                "Complete more learning sessions to identify "
                "your performance trends."
            ),
            "total_sessions": total_sessions,
            "recent_average": None,
            "previous_average": None,
            "score_difference": None,
            "trend": "Not Available"
        }

    # Use the five most recent sessions.
    recent_sessions = sessions[:5]

    # Compare them with the five sessions before that.
    previous_sessions = sessions[5:10]

    if not previous_sessions:
        return {
            "status": "Insufficient Data",
            "message": (
                "More learning sessions are needed to compare "
                "recent performance with earlier performance."
            ),
            "total_sessions": total_sessions,
            "recent_average": round(
                sum(s["score_percentage"] for s in recent_sessions)
                / len(recent_sessions),
                2
            ),
            "previous_average": None,
            "score_difference": None,
            "trend": "Not Available"
        }

    recent_average = sum(
        session["score_percentage"]
        for session in recent_sessions
    ) / len(recent_sessions)

    previous_average = sum(
        session["score_percentage"]
        for session in previous_sessions
    ) / len(previous_sessions)

    difference = recent_average - previous_average

    # Ignore small fluctuations of less than 5 percentage points.
    if difference >= 5:
        trend = "Improving"

        message = (
            "Your recent learning performance has improved "
            "compared with your earlier sessions."
        )

    elif difference <= -5:
        trend = "Declining"

        message = (
            "Your recent performance is lower than your earlier "
            "performance. Reviewing difficult topics may help."
        )

    else:
        trend = "Stable"

        message = (
            "Your learning performance is relatively stable "
            "across recent and earlier sessions."
        )

    return {
        "status": "Analysis Complete",
        "message": message,
        "total_sessions": total_sessions,
        "recent_sessions": len(recent_sessions),
        "previous_sessions": len(previous_sessions),
        "recent_average": round(recent_average, 2),
        "previous_average": round(previous_average, 2),
        "score_difference": round(difference, 2),
        "trend": trend
    }
