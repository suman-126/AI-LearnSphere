import json
import random
import re

from config.settings import (
    QUIZ_DIFFICULTIES,
    AVAILABLE_QUESTION_COUNTS
)

from services.llm_service import generate_response

from modules.quiz_generator.question_bank import (
    PYTHON_VARIABLES_QUESTIONS
)


MAX_GENERATION_ATTEMPTS = 3


def _extract_json(response):
    """Extract a JSON object from the model response."""

    if not isinstance(response, str) or not response.strip():
        raise ValueError("The AI returned an empty response.")

    cleaned = response.strip()

    cleaned = re.sub(
        r"^```(?:json)?\s*|\s*```$",
        "",
        cleaned,
        flags=re.IGNORECASE
    ).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()

    for match in re.finditer(r"\{", cleaned):
        try:
            data, _ = decoder.raw_decode(cleaned[match.start():])
            return data
        except json.JSONDecodeError:
            continue

    raise ValueError("The AI did not return valid JSON.")


def _normalize_text(value):
    """Normalize text for duplicate detection."""

    return re.sub(r"[\W_]+", "", value.casefold())


def _validate_quiz(
    data,
    topic,
    subject,
    difficulty,
    num_questions,
    previous_questions=None
):
    """Validate the complete generated quiz."""

    if not isinstance(data, dict):
        raise ValueError("Invalid quiz response format.")

    questions = data.get("questions")

    if not isinstance(questions, list):
        raise ValueError("The questions list is missing.")

    if len(questions) != num_questions:
        raise ValueError(
            f"Expected {num_questions} questions, "
            f"but received {len(questions)}."
        )

    validated_questions = []
    seen_questions = set()

    previous_question_set = {
       _normalize_text(question)
       for question in (previous_questions or [])
       if isinstance(question, str)
    }

    required_options = {"A", "B", "C", "D"}

    for index, item in enumerate(questions, start=1):

        if not isinstance(item, dict):
            raise ValueError(
                f"Question {index} has an invalid format."
            )

        question = item.get("question")
        options = item.get("options")
        correct_answer = item.get("correct_answer")
        explanation = item.get("explanation")

        if not isinstance(question, str) or not question.strip():
            raise ValueError(
                f"Question {index} text is missing."
            )

        question = question.strip()
        normalized_question = _normalize_text(question)

        if (
            normalized_question in seen_questions
            or normalized_question in previous_question_set
        ):
            raise ValueError(
                f"Duplicate question detected at question {index}."
            )

        if not isinstance(options, dict):
            raise ValueError(
                f"Options are invalid in question {index}."
            )

        if set(options.keys()) != required_options:
            raise ValueError(
                f"Question {index} must have options A, B, C and D."
            )

        if not all(
            isinstance(options[key], str) and options[key].strip()
            for key in ["A", "B", "C", "D"]
        ):
            raise ValueError(
                f"Question {index} contains an empty option."
            )

        normalized_options = [
            _normalize_text(options[key].strip())
            for key in ["A", "B", "C", "D"]
        ]

        if len(set(normalized_options)) != 4:
            raise ValueError(
                f"Duplicate options detected in question {index}."
            )

        if not isinstance(correct_answer, str):
            raise ValueError(
                f"Correct answer is invalid in question {index}."
            )

        correct_answer = correct_answer.strip().upper()

        if correct_answer not in required_options:
            raise ValueError(
                f"Correct answer must be A, B, C or D "
                f"in question {index}."
            )

        if not isinstance(explanation, str) or not explanation.strip():
            raise ValueError(
                f"Explanation is missing in question {index}."
            )

        seen_questions.add(normalized_question)

        validated_questions.append({
            "question": question,
            "options": {
                key: options[key].strip()
                for key in ["A", "B", "C", "D"]
            },
            "correct_answer": correct_answer,
            "explanation": explanation.strip()
        })

    return {
        "subject": subject,
        "topic": topic,
        "difficulty": difficulty,
        "total_questions": len(validated_questions),
        "questions": validated_questions
    }


def _generate_verified_python_variables_quiz(
    subject,
    topic,
    difficulty,
    num_questions,
    previous_questions=None
):
    """Generate a quiz using verified Python Variables questions."""

    previous_question_set = {
       _normalize_text(question)
       for question in (previous_questions or [])
       if isinstance(question, str)
    }

    available_questions = [
        item
        for item in PYTHON_VARIABLES_QUESTIONS
        if _normalize_text(item["question"]) not in previous_question_set
    ]

    if num_questions > len(available_questions):
       raise ValueError(
          f"Only {len(available_questions)} unique questions remain "
          f"in the verified Python Variables question bank. "
          f"Please choose a smaller question count or start a new session."
        )

    selected_questions = random.sample(
        available_questions,
        num_questions
    )

    final_questions = []

    for item in selected_questions:

        correct_text = item["options"][item["correct_answer"]]

        shuffled_options = list(item["options"].values())
        random.shuffle(shuffled_options)

        options = {
            label: option
            for label, option in zip(
                ["A", "B", "C", "D"],
                shuffled_options
            )
        }

        correct_answer = next(
            label
            for label, option in options.items()
            if option == correct_text
        )

        final_questions.append({
            "question": item["question"],
            "options": options,
            "correct_answer": correct_answer,
            "explanation": item["explanation"]
        })

    quiz = {
        "subject": subject,
        "topic": topic,
        "difficulty": difficulty,
        "total_questions": len(final_questions),
        "questions": final_questions
    }

    return quiz


def generate_quiz(
    topic,
    subject=None,
    difficulty="Beginner",
    num_questions=10,
    previous_questions=None
):
    """Generate and validate a complete multiple-choice quiz."""

    if not isinstance(topic, str) or not topic.strip():
        raise ValueError("Please provide a valid quiz topic.")

    if subject is not None and not isinstance(subject, str):
        raise ValueError("Subject must be a string.")

    if difficulty not in QUIZ_DIFFICULTIES:
        raise ValueError(
            f"Difficulty must be one of: {QUIZ_DIFFICULTIES}"
        )

    if num_questions not in AVAILABLE_QUESTION_COUNTS:
        raise ValueError(
            f"Number of questions must be one of: "
            f"{AVAILABLE_QUESTION_COUNTS}"
        )

    topic = topic.strip()

    subject_text = (
        subject.strip()
        if subject and subject.strip()
        else "General"
    )

    previous_questions = previous_questions or []

    is_python_variables = (
        "python" in f"{subject_text} {topic}".casefold()
        and "variable" in topic.casefold()
    )

    # Use verified questions for Beginner Python Variables.
    if is_python_variables and difficulty == "Beginner":

        quiz = _generate_verified_python_variables_quiz(
            subject=subject_text,
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions,
            previous_questions=previous_questions
        )

        return quiz

    # Use Llama for other topics and difficulty levels.
    system_prompt = (
        "You are an expert educational assessment designer. "
        "Generate accurate, relevant and varied multiple-choice "
        "questions. Follow the requested JSON schema exactly. "
        "Return only valid JSON without Markdown."
    )

    prompt = f"""
Create exactly {num_questions} multiple-choice questions.

SUBJECT: {subject_text}
TOPIC: {topic}
DIFFICULTY: {difficulty}

PREVIOUSLY USED QUESTIONS:
{json.dumps(previous_questions, ensure_ascii=False)}

Do not repeat any previously used question, including reworded versions.

REQUIREMENTS:

1. Every question must directly test the selected topic.
2. Cover different concepts and aspects.
3. Do not repeat or rephrase questions.
4. Use clear educational language.
5. Every question must have exactly four options.
6. Label options A, B, C and D.
7. All options must be meaningfully different.
8. Only one option must be correct.
9. Ensure the correct answer matches the explanation.
10. Explanations must be factually accurate.
11. Avoid ambiguous questions.
12. Include code snippets when necessary.
13. Match the selected difficulty.
14. Do not invent facts or syntax.

Return ONLY one JSON object in this exact structure:

{{
    "questions": [
        {{
            "question": "Question text",
            "options": {{
                "A": "First option",
                "B": "Second option",
                "C": "Third option",
                "D": "Fourth option"
            }},
            "correct_answer": "A",
            "explanation": "Explanation of the correct answer."
        }}
    ]
}}

The questions array must contain exactly {num_questions} objects.
Do not include additional properties or text.
"""

    last_error = None

    for attempt in range(1, MAX_GENERATION_ATTEMPTS + 1):

        try:

            current_prompt = prompt

            if attempt > 1:
                current_prompt += f"""

Your previous quiz failed validation.

Problem: {last_error}

Generate the complete quiz again.
Fix the validation problem.
Follow the JSON structure exactly.
"""

            response = generate_response(
                prompt=current_prompt,
                system_prompt=system_prompt,
                model="llama3.2:latest",
                temperature=0.2
            )

            quiz_data = _extract_json(response)

            validated_quiz = _validate_quiz(
                data=quiz_data,
                topic=topic,
                subject=subject_text,
                difficulty=difficulty,
                num_questions=num_questions,
                previous_questions=previous_questions
            )

            return validated_quiz

        except ValueError as error:

            last_error = error

            print(
                f"Quiz generation attempt {attempt} failed: {error}"
            )

    raise ValueError(
        f"Could not generate a valid quiz after "
        f"{MAX_GENERATION_ATTEMPTS} attempts. "
        f"Last error: {last_error}"
    )


def evaluate_quiz(quiz, user_answers):
    """Evaluate submitted answers and calculate quiz performance."""

    if not isinstance(quiz, dict) or not isinstance(
        quiz.get("questions"), list
    ):
        raise ValueError("Invalid quiz data.")

    questions = quiz["questions"]

    if not isinstance(user_answers, dict):
        raise ValueError("User answers must be provided as a dictionary.")

    total_questions = len(questions)

    if total_questions == 0:
        raise ValueError("The quiz contains no questions.")

    results = []
    correct_count = 0

    for index, question in enumerate(questions):

        correct_answer = question["correct_answer"]

        submitted_answer = user_answers.get(index)

        if submitted_answer is not None:
            submitted_answer = str(submitted_answer).strip().upper()

        is_correct = submitted_answer == correct_answer

        if is_correct:
            correct_count += 1

        results.append({
            "question": question["question"],
            "user_answer": submitted_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": question["explanation"]
        })

    incorrect_count = total_questions - correct_count

    percentage = round(
        (correct_count / total_questions) * 100,
        2
    )

    return {
        "total_questions": total_questions,
        "correct_answers": correct_count,
        "incorrect_answers": incorrect_count,
        "percentage": percentage,
        "results": results
    }


def generate_quiz_result(evaluation):
    """Format quiz evaluation into a readable result."""

    if not isinstance(evaluation, dict):
        raise ValueError("Invalid quiz evaluation data.")

    required_keys = [
        "total_questions",
        "correct_answers",
        "incorrect_answers",
        "percentage",
        "results"
    ]

    for key in required_keys:
        if key not in evaluation:
            raise ValueError(
                f"Missing evaluation field: {key}"
            )

    total = evaluation["total_questions"]
    correct = evaluation["correct_answers"]
    incorrect = evaluation["incorrect_answers"]
    percentage = evaluation["percentage"]

    if total <= 0 or correct + incorrect != total:
        raise ValueError("Quiz evaluation totals are invalid.")

    if not 0 <= percentage <= 100:
        raise ValueError("Invalid quiz percentage.")

    if not isinstance(evaluation["results"], list):
        raise ValueError("Detailed results must be a list.")

    if len(evaluation["results"]) != total:
        raise ValueError("Detailed results count does not match.")

    if percentage >= 80:
        performance = "Excellent"
        message = "Great work! You have a strong understanding."
    elif percentage >= 60:
        performance = "Good"
        message = "Good effort! Review the incorrect answers."
    elif percentage >= 40:
        performance = "Needs Improvement"
        message = "Keep practising to strengthen your understanding."
    else:
        performance = "Keep Practising"
        message = "Review the topic and try another quiz."

    return {
        "performance": performance,
        "message": message,
        "summary": {
            "total_questions": total,
            "correct_answers": correct,
            "incorrect_answers": incorrect,
            "percentage": percentage
        },
        "detailed_results": evaluation["results"]
    }
