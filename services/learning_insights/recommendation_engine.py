from services.learning_insights.insights_analyzer import (
    get_performance_analysis
)

from services.learning_insights.trend_analyzer import (
    analyze_learning_trends
)

def generate_recommendations():
    """
    Generate personalized learning recommendations
    using actual quiz and practice performance.
    """

    analysis = get_performance_analysis()
    trends = analyze_learning_trends()

    topic_performance = analysis["topic_performance"]

    recommendations = []

    # Identify topics that need improvement.
    for topic in topic_performance:

        attempts = topic["attempts"]
        score = topic["average_score"]
        subject = topic["subject"]
        topic_name = topic["topic"]

        # Require at least two attempts for reliable classification.
        if attempts < 2:
            continue

        if score < 50:
            recommendations.append({
                "priority": "High",
                "category": "Topic Improvement",
                "subject": subject,
                "topic": topic_name,
                "score": score,
                "suggestion": (
                    f"Review the fundamentals of {topic_name} "
                    f"in {subject}, then complete additional "
                    "practice questions."
                )
            })

        elif score < 70:
            recommendations.append({
                "priority": "Medium",
                "category": "Topic Practice",
                "subject": subject,
                "topic": topic_name,
                "score": score,
                "suggestion": (
                    f"Strengthen your understanding of {topic_name} "
                    f"in {subject} through revision and regular practice."
                )
            })

        elif score >= 80:
            recommendations.append({
                "priority": "Low",
                "category": "Strength Maintenance",
                "subject": subject,
                "topic": topic_name,
                "score": score,
                "suggestion": (
                    f"Continue practising {topic_name} in {subject} "
                    "and gradually explore more advanced questions."
                )
            })

    # Add a recommendation based on overall learning trends.
    if trends["trend"] == "Declining":
        recommendations.append({
            "priority": "High",
            "category": "Learning Trend",
            "subject": None,
            "topic": None,
            "score": trends["score_difference"],
            "suggestion": (
                "Your recent performance has declined. "
                "Review your recent mistakes and revisit "
                "the topics you find difficult."
            )
        })

    elif trends["trend"] == "Improving":
        recommendations.append({
            "priority": "Low",
            "category": "Learning Trend",
            "subject": None,
            "topic": None,
            "score": trends["score_difference"],
            "suggestion": (
                "Your performance is improving. Maintain your "
                "learning routine and gradually attempt more "
                "challenging questions."
            )
        })

    # Sort recommendations by priority.
    priority_order = {
        "High": 1,
        "Medium": 2,
        "Low": 3
    }

    recommendations.sort(
        key=lambda item: priority_order[item["priority"]]
    )

    if not analysis["overall"]["total_sessions"]:
        message = (
            "Complete some Smart Quiz or Practice Arena sessions "
            "to receive personalized recommendations."
        )

    elif not recommendations:
        message = (
            "There is not enough repeated topic-level performance "
            "data to identify specific recommendations yet. "
            "Continue learning and practising."
        )

    else:
        message = (
            "Recommendations have been generated using "
            "your saved learning performance."
        )

    return {
        "status": "Analysis Complete",
        "message": message,
        "total_recommendations": len(recommendations),
        "recommendations": recommendations
    }
