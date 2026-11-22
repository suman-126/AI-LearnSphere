import json
import re

from services.llm_service import generate_response
from config.settings import (
    DEFAULT_LLM_MODEL,
    QUIZ_DIFFICULTIES
)


def _extract_json(response):
    """Extract a JSON object from the model response."""

    if not isinstance(response, str) or not response.strip():
        raise ValueError("The AI returned an empty response.")

    cleaned = response.strip()

    # Remove optional Markdown code fences.
    cleaned = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(r"\s*```$", "", cleaned)

    start = cleaned.find("{")
    end = cleaned.rfind("}")

    if start == -1 or end == -1 or end <= start:
        raise ValueError("The AI did not return valid JSON.")

    try:
        result = json.loads(cleaned[start:end + 1])
    except json.JSONDecodeError as error:
        raise ValueError(
            "The AI returned incorrectly formatted JSON."
        ) from error

    if not isinstance(result, dict):
        raise ValueError("The AI response must be a JSON object.")

    return result


def generate_assessment(
    subject,
    topic,
    difficulty="Beginner"
):
    """Generate a written knowledge assessment."""

    if not isinstance(subject, str) or not subject.strip():
        raise ValueError("Please provide a valid subject.")

    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("Please provide a valid topic.")

    if difficulty not in QUIZ_DIFFICULTIES:
        raise ValueError("Invalid assessment difficulty.")

    system_prompt = """
You are an expert academic assessment designer.

Create one accurate, clear, topic-specific written assessment.

Return ONLY a valid JSON object with these fields:
{
    "question": "One assessment question",
    "reference_answer": "A correct and complete reference answer",
    "key_concepts": [
        "Important concept 1",
        "Important concept 2",
        "Important concept 3"
    ]
}

Requirements:
- Match the requested difficulty.
- Test conceptual understanding, not just memorisation.
- The question must be answerable without external resources.
- The reference answer must be factually accurate.
- Include 3 to 5 relevant key concepts.
- Do not include multiple-choice options.
- Do not invent facts.
"""

    prompt = f"""
Create a written knowledge assessment.

Subject: {subject.strip()}
Topic: {topic.strip()}
Difficulty: {difficulty}

Return the required JSON object only.
"""

    response = generate_response(
        prompt=prompt,
        system_prompt=system_prompt,
        model=DEFAULT_LLM_MODEL,
        temperature=0.2
    )

    assessment = _extract_json(response)

    question = assessment.get("question")
    reference_answer = assessment.get("reference_answer")
    key_concepts = assessment.get("key_concepts")

    if not isinstance(question, str) or not question.strip():
        raise ValueError("The generated question is invalid.")

    if not isinstance(reference_answer, str) or not reference_answer.strip():
        raise ValueError("The reference answer is invalid.")

    if not isinstance(key_concepts, list) or not 3 <= len(key_concepts) <= 5:
        raise ValueError("The generated key concepts are invalid.")

    if not all(
        isinstance(concept, str) and concept.strip()
        for concept in key_concepts
    ):
        raise ValueError("One or more key concepts are invalid.")

    return {
        "subject": subject.strip(),
        "topic": topic.strip(),
        "difficulty": difficulty,
        "question": question.strip(),
        "reference_answer": reference_answer.strip(),
        "key_concepts": key_concepts
    }


def evaluate_knowledge(
    assessment,
    learner_answer, model=None
):
    """Evaluate a learner's written answer."""

    if not isinstance(assessment, dict):
        raise ValueError("Invalid assessment data.")

    required_fields = [
        "subject",
        "topic",
        "question",
        "reference_answer",
        "key_concepts"
    ]

    for field in required_fields:
        if field not in assessment:
            raise ValueError(
                f"Assessment is missing the field: {field}"
            )

    if not isinstance(learner_answer, str) or not learner_answer.strip():
        raise ValueError("Please provide your written answer.")

    
    system_prompt = """
    You are a fair, accurate, and consistent academic evaluator.

    Evaluate the learner's answer using ONLY the assessment question,
    reference answer, and supplied key concepts.

    Return ONLY a valid JSON object with this structure:

    {
       "score": 75,
       "understanding": "Good",
       "strengths": [
           "Concepts correctly explained"
        ],
        "knowledge_gaps": [
            "Concepts missing or incorrectly explained"
        ],
       "feedback": "Specific feedback about the answer",
       "improvement_suggestions": [
           "Suggestion for improvement"
        ]
    }

    Evaluation rules:
    - Score must be an integer from 0 to 100.
    - Evaluate conceptual understanding, not exact wording.
    - Accept correct explanations written in the learner's own words.
    - Do not penalise minor grammar or spelling mistakes.
    - Do not award marks for unrelated content.
    - Be fair to short but correct answers.
    - Evaluate only the concepts listed in the supplied key concepts.
    - Do not introduce additional requirements or missing concepts.
    - Do not identify a concept as missing if the learner has
      already explained it correctly.
    - Do not invent mistakes or knowledge gaps.
    - Give credit for correct examples and explanations.
    - Keep feedback educational and constructive.
    - Do not automatically award full marks.
    - Return valid JSON only.
    - Check every supplied key concept individually against the learner's answer.
    - If all key concepts are correctly explained, return an empty knowledge_gaps list.
    - Do not create generic knowledge gaps when no required concept is missing.
    - If all key concepts are covered, do not suggest adding more detail
      unless the reference answer requires an important missing explanation.
    - Keep the score consistent with the concepts demonstrated.
    """

    prompt = f"""
Evaluate the following written assessment.

Subject: {assessment['subject']}
Topic: {assessment['topic']}

Question:
{assessment['question']}

Reference Answer:
{assessment['reference_answer']}

Key Concepts:
{json.dumps(assessment['key_concepts'], ensure_ascii=False)}

Learner's Answer:
{learner_answer.strip()}

Evaluate the answer using the required JSON structure.
"""

    response = generate_response(
        prompt=prompt,
        system_prompt=system_prompt,
        model=model or "phi3:mini",
        temperature=0.1
    )

    result = _extract_json(response)

    score = result.get("score")

    if (
        isinstance(score, bool)
        or not isinstance(score, (int, float))
        or not 0 <= score <= 100
    ):
        raise ValueError("The AI returned an invalid assessment score.")

    
    understanding = result.get("understanding")

    if isinstance(understanding, str):
       normalized_understanding = understanding.strip().lower()

       understanding_levels = {
            "excellent": "Excellent",
            "good": "Good",
            "developing": "Developing",
            "needs improvement": "Needs Improvement",
            "poor": "Needs Improvement",
            "fair": "Developing",
            "average": "Developing"
        }

       understanding = understanding_levels.get(
           normalized_understanding
        )

    if understanding is None:
       if score >= 85:
          understanding = "Excellent"
       elif score >= 70:
           understanding = "Good"
       elif score >= 50:
           understanding = "Developing"
       else:
           understanding = "Needs Improvement"

    list_fields = [
        "strengths",
        "knowledge_gaps",
        "improvement_suggestions"
    ]

    for field in list_fields:
        if not isinstance(result.get(field), list):
            raise ValueError(
                f"The AI returned an invalid {field} list."
            )

        if not all(
            isinstance(item, str) and item.strip()
            for item in result[field]
        ):
            raise ValueError(
                f"The AI returned invalid items in {field}."
            )

    feedback = result.get("feedback")

    if not isinstance(feedback, str) or not feedback.strip():
        raise ValueError("The AI returned invalid feedback.")

    return {
        "subject": assessment["subject"],
        "topic": assessment["topic"],
        "score": round(score, 2),
        "understanding": understanding,
        "strengths": result["strengths"],
        "knowledge_gaps": result["knowledge_gaps"],
        "feedback": feedback.strip(),
        "improvement_suggestions": result["improvement_suggestions"]
    }
