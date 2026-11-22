# ==========================================
# AI LEARNSPHERE - PYTHON CODE EVALUATOR
# ==========================================
import json
import re

from services.llm_service import generate_response
from modules.practice_arena.static_analyzer import (
    analyze_code_submission
)


def _extract_json(response):
    """Extract a JSON object from the AI response."""

    if not isinstance(response, str) or not response.strip():
        raise ValueError("The AI returned an empty response.")

    cleaned_response = response.strip()

    cleaned_response = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned_response,
        flags=re.IGNORECASE
    )

    cleaned_response = re.sub(
        r"\s*```$",
        "",
        cleaned_response
    )

    try:
        result = json.loads(cleaned_response)

    except json.JSONDecodeError:

        match = re.search(
            r"\{.*\}",
            cleaned_response,
            re.DOTALL
        )

        if not match:
            raise ValueError(
                "Could not find valid JSON in the AI response."
            )

        try:
            result = json.loads(match.group())

        except json.JSONDecodeError as error:
            raise ValueError(
                "The AI returned incorrectly formatted JSON."
            ) from error

    if not isinstance(result, dict):
        raise ValueError("The AI response must contain a JSON object.")

    return result


def evaluate_code_submission(
    challenge,
    submitted_code,
    model=None
):
    """
    Evaluate a Python coding challenge using static analysis
    and AI-based code review.

    Submitted code is never executed.
    """

    if not isinstance(challenge, dict):
        raise ValueError("Invalid coding challenge.")

    if not isinstance(submitted_code, str) or not submitted_code.strip():
        raise ValueError("Please submit your Python code.")

    required_fields = [
        "title",
        "description",
        "difficulty",
        "expected_concepts",
        "example_input",
        "example_output"
    ]

    for field in required_fields:
        if field not in challenge:
            raise ValueError(
                f"Coding challenge is missing: {field}"
            )

    # Step 1: Perform static analysis.
    static_result = analyze_code_submission(
        challenge,
        submitted_code
    )

    # Stop AI evaluation if Python syntax is invalid.
    if not static_result["syntax_valid"]:

        return {
            "score": 0,
            "correctness": "Needs Improvement",
            "concept_coverage": "Limited",
            "code_quality": "Needs Improvement",
            "strengths": [],
            "issues": static_result["issues"],
            "feedback": (
                "Your submission contains Python syntax errors. "
                "Please correct them before evaluation."
            ),
            "suggestions": [
                "Review the reported syntax errors and correct them."
            ],
            "static_analysis": static_result
        }

    # Step 2: Prepare AI evaluation instructions.
    system_prompt = """
You are a fair and experienced Python programming instructor.

Evaluate the learner's code according to the actual challenge.

IMPORTANT RULES:

1. Never execute the submitted code.
2. Focus on the stated challenge requirements.
3. Accept different valid programming approaches.
4. Do not penalize missing type hints, comments or docstrings.
5. Do not demand unnecessary error handling.
6. Do not invent errors.
7. Consider the static analysis findings carefully.
8. Do not ignore a clear logical issue reported by static analysis.
9. Distinguish genuine problems from optional improvements.
10. Never claim that execution tests have passed.

SCORING:

90-100: Correct solution satisfying the requirements.
75-89: Mostly correct with minor issues.
50-74: Partially correct with meaningful gaps.
25-49: Substantially incomplete or incorrect.
0-24: Unrelated, empty or fundamentally incorrect.

A correct beginner solution deserves a high score.

Return only valid JSON:

{
    "score": 95,
    "correctness": "Strong",
    "concept_coverage": "Good",
    "code_quality": "Good",
    "strengths": [],
    "issues": [],
    "feedback": "",
    "suggestions": []
}

Allowed values:
correctness: Strong, Partial, Needs Improvement
concept_coverage: Good, Partial, Limited
code_quality: Good, Average, Needs Improvement

All list fields must contain strings.
Score must be an integer from 0 to 100.
"""

    prompt = f"""
Evaluate this Python coding challenge submission.

CHALLENGE:
Title: {challenge['title']}
Difficulty: {challenge['difficulty']}

Description:
{challenge['description']}

Example Input:
{challenge['example_input']}

Expected Output:
{challenge['example_output']}

Expected Concepts:
{json.dumps(challenge['expected_concepts'], ensure_ascii=False)}

STATIC ANALYSIS FINDINGS:
{json.dumps(static_result, indent=4, ensure_ascii=False)}

LEARNER'S CODE:
{submitted_code}

Consider the static analysis findings alongside your own review.

Return only the required JSON object.
"""

    # Step 3: Request AI review.
    response = generate_response(
        prompt=prompt,
        system_prompt=system_prompt,
        model=model,
        temperature=0.1
    )

    result = _extract_json(response)

    required_result_fields = [
        "score",
        "correctness",
        "concept_coverage",
        "code_quality",
        "strengths",
        "issues",
        "feedback",
        "suggestions"
    ]

    for field in required_result_fields:
        if field not in result:
            raise ValueError(
                f"AI evaluation is missing the field: {field}"
            )

    # Step 4: Validate the AI score.
    try:
        score = int(result["score"])
    except (ValueError, TypeError):
        raise ValueError("AI returned an invalid evaluation score.")

    result["score"] = max(0, min(100, score))

    # Step 5: Validate evaluation labels.
    allowed_values = {
        "correctness": [
            "Strong",
            "Partial",
            "Needs Improvement"
        ],
        "concept_coverage": [
            "Good",
            "Partial",
            "Limited"
        ],
        "code_quality": [
            "Good",
            "Average",
            "Needs Improvement"
        ]
    }

    for field, allowed in allowed_values.items():
        if result[field] not in allowed:
            result[field] = "Partial"

    if not isinstance(result["feedback"], str):
        raise ValueError("AI returned invalid feedback.")

    # Step 6: Normalize feedback lists.
    for field in ["strengths", "issues", "suggestions"]:
        if not isinstance(result[field], list):
            result[field] = []

        result[field] = [
            str(item) for item in result[field]
        ]

    # Step 7: Apply clear static-analysis findings.
    # Step 7: Apply clear static-analysis findings.
    static_issues = static_result["issues"]

    if static_issues:

       result["issues"] = list(dict.fromkeys(
          result["issues"] + static_issues
       ))

       result["score"] = min(result["score"], 49)

       result["correctness"] = "Needs Improvement"

       # Avoid contradictory AI-generated strengths.
       result["strengths"] = [
          "Python syntax is valid."
        ]

       # Give feedback based on the actual static findings.
       result["feedback"] = (
           "Static analysis identified a potential logical issue: "
           + " ".join(static_issues)
           + " Please correct this issue and review your solution."
        )

       result["suggestions"] = [
           "Correct the identified logical issue.",
           "Review the challenge requirements before resubmitting."
        ]

    # Include static analysis details in the final result.
    result["static_analysis"] = static_result

    return result
