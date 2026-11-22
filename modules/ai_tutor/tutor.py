
from services.llm_service import (
    generate_response,
    generate_chat_response
)

from config.settings import (
    DEFAULT_LEARNING_LEVEL,
    DEFAULT_EXPLANATION_STYLE,
    LEARNING_LEVELS,
    EXPLANATION_STYLES
)


def build_tutor_system_prompt(
    subject=None,
    learning_level=DEFAULT_LEARNING_LEVEL,
    explanation_style=DEFAULT_EXPLANATION_STYLE
):
    """Build concise system instructions for the AI Tutor."""

    if learning_level not in LEARNING_LEVELS:
        raise ValueError("Invalid learning level.")

    if explanation_style not in EXPLANATION_STYLES:
        raise ValueError("Invalid explanation style.")

    system_prompt = (
        "You are AI LearnSphere, an educational AI tutor. "
        "Help students understand concepts accurately and clearly. "
        "Always respond in English.\n\n"
    )

    if subject and subject.strip():
        system_prompt += f"Subject: {subject.strip()}\n"

    system_prompt += f"Learning level: {learning_level}\n"
    system_prompt += f"Explanation style: {explanation_style}\n\n"

    system_prompt += (
         "IMPORTANT CONVERSATION RULES:\n"
         "1. Always answer the student's latest question first.\n"
         "2. Treat previous messages only as context for understanding "
         "the current question.\n"
         "3. Do not answer an earlier question again unless the student "
         "explicitly asks for a repetition or clarification.\n"
         "4. Do not repeat previous explanations unnecessarily.\n"
         "5. Explain the exact concept asked about, not merely a related "
         "concept.\n"
         "6. Use clear language and relevant examples.\n"
         "7. For programming questions, ensure code examples are "
         "syntactically valid and logically correct.\n"
         "8. Check that function arguments, parameters, return values, "
         "and variable names are used consistently.\n"
         "9. When writing decorators, ensure wrapper functions correctly "
         "accept and forward arguments using *args and **kwargs when needed.\n"
         "10. Verify the example's expected output before presenting it.\n"
         "11. Avoid unnecessary repetition and do not invent facts.\n\n"
    )

    if explanation_style == "Simple":
        system_prompt += (
            "Explain using simple words, short sentences, "
            "and beginner-friendly examples."
        )

    elif explanation_style == "Detailed":
        system_prompt += (
            "Explain the concept thoroughly, including how and why "
            "it works. Use examples where useful."
        )

    else:
        system_prompt += (
            "First provide a simple explanation, then provide "
            "a deeper explanation with a useful example."
        )

    return system_prompt


def ask_tutor(
    question,
    subject=None,
    learning_level=DEFAULT_LEARNING_LEVEL,
    explanation_style=DEFAULT_EXPLANATION_STYLE,
    language="English",
    model=None,
    conversation_history=None
):
    """Generate an educational response using the AI Tutor."""

    if not isinstance(question, str) or not question.strip():
        raise ValueError("Question cannot be empty.")

    if language != "English":
        raise ValueError("AI Tutor currently supports English only.")

    system_prompt = build_tutor_system_prompt(
        subject=subject,
        learning_level=learning_level,
        explanation_style=explanation_style
    )

    # First question: send the original question separately.
    if not conversation_history:
        return generate_response(
            prompt=question.strip(),
            system_prompt=system_prompt,
            model=model,
            temperature=0.2
        )

    # Follow-up question: preserve the previous conversation.
    if not isinstance(conversation_history, list):
        raise ValueError("Conversation history must be a list.")

    messages = conversation_history[-4:].copy()

    for message in messages:
        if not isinstance(message, dict):
            raise ValueError("Invalid conversation message.")

        if message.get("role") not in ["user", "assistant"]:
            raise ValueError("Invalid conversation message role.")

        if (
            not isinstance(message.get("content"), str)
            or not message["content"].strip()
        ):
            raise ValueError("Conversation message cannot be empty.")

    messages.append({
        "role": "user",
        "content": question.strip()
    })

    return generate_chat_response(
        messages=messages,
        system_prompt=system_prompt,
        model=model,
        temperature=0.2
    )
