
from services.storage_manager import (
    get_quiz_results,
    get_topic_progress
)


def get_overall_performance():
    """Calculate overall quiz performance."""

    results = get_quiz_results()

    if not results:
        return {
            "total_quizzes": 0,
            "total_questions": 0,
            "correct_answers": 0,
            "average_score": 0.0
        }

    total_questions = sum(
        result["total_questions"] for result in results
    )

    correct_answers = sum(
        result["correct_answers"] for result in results
    )

    average_score = sum(
        result["score_percentage"] for result in results
    ) / len(results)

    return {
        "total_quizzes": len(results),
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "average_score": round(average_score, 2)
    }


def get_subject_performance():
    """Calculate average quiz performance for each subject."""

    results = get_quiz_results()
    subject_scores = {}

    for result in results:
        subject = result["subject"]

        if subject not in subject_scores:
            subject_scores[subject] = []

        subject_scores[subject].append(
            result["score_percentage"]
        )

    performance = {}

    for subject, scores in subject_scores.items():
        performance[subject] = round(
            sum(scores) / len(scores), 2
        )

    return performance


def get_topic_performance():
    """Calculate average quiz performance for each topic."""

    results = get_quiz_results()
    topic_scores = {}

    for result in results:
        topic = (result["subject"], result["topic"])

        if topic not in topic_scores:
            topic_scores[topic] = []

        topic_scores[topic].append(
            result["score_percentage"]
        )

    performance = {}

    for (subject, topic), scores in topic_scores.items():
        performance[f"{subject} - {topic}"] = round(
            sum(scores) / len(scores), 2
        )

    return performance


def identify_strong_and_weak_topics():
    """Identify topics based on average quiz scores."""

    performance = get_topic_performance()

    strong_topics = []
    weak_topics = []

    for topic, score in performance.items():

        if score >= 75:
            strong_topics.append({
                "topic": topic,
                "score": score
            })

        elif score < 50:
            weak_topics.append({
                "topic": topic,
                "score": score
            })

    return {
        "strong_topics": strong_topics,
        "weak_topics": weak_topics
    }


def get_learning_progress_summary():
    """Combine quiz performance and topic progress."""

    overall = get_overall_performance()
    subjects = get_subject_performance()
    topics = get_topic_progress()
    strengths = identify_strong_and_weak_topics()

    return {
        "overall_performance": overall,
        "subject_performance": subjects,
        "topic_progress": topics,
        "strong_and_weak_topics": strengths
    }
