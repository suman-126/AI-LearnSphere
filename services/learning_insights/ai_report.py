import json

from services.llm_service import generate_response

from services.learning_insights.insights_analyzer import (
    get_performance_analysis
)

from services.learning_insights.trend_analyzer import (
    analyze_learning_trends
)

from services.learning_insights.recommendation_engine import (
    generate_recommendations
)

SYSTEM_PROMPT = """
You are a study guidance assistant inside AI LearnSphere.

Your task is to provide practical learning advice based
on the learner's supplied learning data.

STRICT RULES:

1. Do not generate or repeat performance scores.
2. Do not assign performance classifications.
3. Do not describe performance as strong, weak, excellent,
   stable, improving, declining, or mastered.
4. Do not make claims about the learner's abilities
   or past performance.
5. Do not invent subjects, topics, attempts, or activities.
6. Focus only on practical study actions.
7. Suggestions should be specific, realistic, and achievable.
8. Avoid repeating the same advice.
9. Use clear, concise bullet points.
10. Return only a heading called "Additional Study Guidance"
    followed by useful bullet points.
"""

def classify_performance(score):
    """Classify learning performance using fixed score ranges."""

    if score < 50:
        return "Needs Improvement"
    elif score < 70:
        return "Developing"
    elif score < 80:
        return "Good Progress"
    else:
        return "Strong Performance"
    

def generate_ai_learning_report(model=None):
    """
    Generate a reliable learning report.

    Python generates factual analytics.
    The local AI model generates additional study guidance.
    """

    analysis = get_performance_analysis()
    trends = analyze_learning_trends()
    recommendations = generate_recommendations()

    if analysis["overall"]["total_sessions"] == 0:
        return (
            "## Learning Insights\n\n"
            "There is not enough saved learning activity to "
            "generate a personalized report yet.\n\n"
            "Complete a Smart Quiz or Practice Arena session "
            "to begin tracking your learning performance."
        )

    overall = analysis["overall"]

    # ------------------------------------------
    # 1. OVERALL PERFORMANCE
    # ------------------------------------------

    overall_level = classify_performance(
        overall["overall_accuracy"]
    )

    report = []

    report.append("## 1. Overall Learning Performance\n")

    report.append(
        f'- **Learning Sessions:** {overall["total_sessions"]}'
    )
    report.append(
        f'- **Questions Answered:** {overall["total_questions"]}'
    )
    report.append(
        f'- **Correct Answers:** {overall["correct_answers"]}'
    )
    report.append(
        f'- **Overall Accuracy:** {overall["overall_accuracy"]:.1f}%'
    )
    report.append(
        f'- **Performance Level:** {overall_level}'
    )
    report.append(
        f'- **Average Session Score:** '
        f'{overall["average_session_score"]:.1f}%'
    )

    # ------------------------------------------
    # 2. SUBJECT PERFORMANCE
    # ------------------------------------------

    report.append("\n## 2. Subject-wise Performance\n")

    for subject in analysis["subject_performance"]:

        level = classify_performance(
            subject["average_score"]
        )

        report.append(f'### {subject["subject"]}')
        report.append(f'- Attempts: {subject["attempts"]}')
        report.append(f'- Questions: {subject["total_questions"]}')
        report.append(
            f'- Correct Answers: {subject["correct_answers"]}'
        )
        report.append(
            f'- Accuracy: {subject["average_score"]:.1f}%'
        )
        report.append(f'- Performance Level: {level}')

    # ------------------------------------------
    # 3. TOPIC PERFORMANCE
    # ------------------------------------------

    report.append(
        "\n## 3. Topic-wise Strengths and Improvement Areas\n"
    )

    for topic in analysis["topic_performance"]:

        level = classify_performance(
            topic["average_score"]
        )

        report.append(
            f'### {topic["subject"]} — {topic["topic"]}'
        )
        report.append(f'- Attempts: {topic["attempts"]}')
        report.append(f'- Questions: {topic["total_questions"]}')
        report.append(
            f'- Correct Answers: {topic["correct_answers"]}'
        )
        report.append(
            f'- Accuracy: {topic["average_score"]:.1f}%'
        )
        report.append(f'- Performance Level: {level}')

        if level == "Needs Improvement":
            report.append(
                '- Focus Area: Review the fundamental concepts '
                'and practice more questions.'
            )
        elif level == "Developing":
            report.append(
                '- Focus Area: Reinforce the concepts through '
                'revision and additional practice.'
            )
        elif level == "Good Progress":
            report.append(
                '- Focus Area: Continue practicing to strengthen '
                'understanding and improve consistency.'
            )
        else:
            report.append(
                '- Focus Area: Continue practicing to maintain '
                'your current performance.'
            )

    # ------------------------------------------
    # 4. LEARNING TREND
    # ------------------------------------------

    report.append("\n## 4. Learning Trend Analysis\n")

    if trends["status"] == "Insufficient Data":

        report.append("**Trend Status:** Insufficient Data")
        report.append(trends["message"])
        report.append(
            "A reliable improving, declining, or stable trend "
            "cannot be determined yet."
        )

    else:

        report.append(
            f'**Learning Trend:** {trends["trend"]}'
        )
        report.append(
            f'Recent Average: {trends["recent_average"]:.1f}%'
        )
        report.append(
            f'Previous Average: {trends["previous_average"]:.1f}%'
        )
        report.append(
            f'Score Difference: '
            f'{trends["score_difference"]:+.1f}%'
        )
        report.append(trends["message"])

    # ------------------------------------------
    # 5. PERSONALIZED RECOMMENDATIONS
    # ------------------------------------------

    report.append("\n## 5. Personalized Recommendations\n")

    recommendation_items = recommendations["recommendations"]

    if recommendation_items:

        for item in recommendation_items:

            category = item.get("category", "")

            subject = item.get("subject")
            topic = item.get("topic")

            # Use a meaningful heading for category-level
            # recommendations such as learning trends.
            if subject and topic:
                heading = f"{subject} — {topic}"
            elif category:
                heading = (
                    "Learning Trend Recommendation"
                    if category == "Learning Trend"
                    else f"{category} Recommendation"
                )
            else:
                heading = "General Learning Recommendation"

            report.append(
                f'### {item["priority"]} Priority: {heading}'
            )

            if category:
                report.append(f'- Category: {category}')

            score = item.get("score")

            if score is not None:

                if category == "Learning Trend":
                    report.append(
                        f'- Score Difference: {score:+.1f}%'
                    )
                else:
                    report.append(
                        f'- Current Score: {score:.1f}%'
                    )

            report.append(
                f'- Suggestion: {item["suggestion"]}'
            )

    else:

        report.append(recommendations["message"])

    # ------------------------------------------
    # 6. AI-GENERATED STUDY GUIDANCE
    # ------------------------------------------

    report.append("\n## 6. AI-Generated Study Guidance\n")

    # Send actionable information to the AI rather than
    # asking it to reinterpret numerical performance data.

    learning_data = {
        "recommendations": [
            {
                "priority": item.get("priority"),
                "subject": item.get("subject"),
                "topic": item.get("topic"),
                "category": item.get("category"),
                "suggestion": item.get("suggestion")
            }
            for item in recommendation_items
        ]
    }

    prompt = f"""
Provide additional practical study guidance
based on these verified learning recommendations.

LEARNING RECOMMENDATIONS:

{json.dumps(learning_data, indent=2, ensure_ascii=False)}

Do not calculate or mention performance scores.
Do not assign performance classifications.
Do not invent subjects or topics.
Provide useful, specific study actions.
Avoid repeating the supplied recommendations.
"""

    try:

        ai_guidance = generate_response(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            model=model,
            temperature=0.2
        )

        if not ai_guidance:
            ai_guidance = (
                "AI study guidance is currently unavailable."
            )

    except Exception as error:

        ai_guidance = (
            "AI study guidance is currently unavailable. "
            "The verified learning analytics above are still available.\n\n"
            f"Reason: {error}"
        )

    report.append(ai_guidance)

    return "\n".join(report)