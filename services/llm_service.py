import requests
from config.settings import (
    OLLAMA_BASE_URL,
    DEFAULT_LLM_MODEL
)


def check_ollama_connection():
    """Check whether the Ollama server is running."""

    try:
        response = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags",
            timeout=10
        )

        response.raise_for_status()
        return True

    except requests.RequestException:
        return False


def get_available_models():
    """Return the model names available in Ollama."""

    try:
        response = requests.get(
            f"{OLLAMA_BASE_URL}/api/tags",
            timeout=10
        )

        response.raise_for_status()

        models = response.json().get("models", [])

        return [
            model.get("name")
            for model in models
            if model.get("name")
        ]

    except requests.RequestException as error:
        raise ConnectionError(
            f"Could not connect to Ollama: {error}"
        ) from error


def generate_response(
    prompt,
    system_prompt=None,
    model=None,
    temperature=0.3
):
    """Generate a response using a local Ollama model."""

    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    selected_model = model or DEFAULT_LLM_MODEL

    payload = {
        "model": selected_model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }

    if system_prompt:
        payload["system"] = system_prompt

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json=payload,
            timeout=180
        )

        response.raise_for_status()

        result = response.json()

        return result.get("response", "").strip()

    except requests.RequestException as error:
        raise ConnectionError(
            f"Ollama response generation failed: {error}"
        ) from error


def generate_chat_response(
    messages,
    system_prompt=None,
    model=None,
    temperature=0.3
):
    """Generate a response using Ollama's conversation API."""

    if not isinstance(messages, list) or not messages:
        raise ValueError("Conversation messages cannot be empty.")

    for message in messages:
        if not isinstance(message, dict):
            raise ValueError("Every message must be a dictionary.")

        if message.get("role") not in ["user", "assistant"]:
            raise ValueError("Invalid conversation message role.")

        if not isinstance(message.get("content"), str) or not message["content"].strip():
            raise ValueError("Message content cannot be empty.")

    selected_model = model or DEFAULT_LLM_MODEL

    chat_messages = []

    if system_prompt:
        chat_messages.append({
            "role": "system",
            "content": system_prompt
        })

    chat_messages.extend(messages)

    payload = {
        "model": selected_model,
        "messages": chat_messages,
        "stream": False,
        "options": {
            "temperature": temperature
        }
    }

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json=payload,
            timeout=180
        )

        response.raise_for_status()

        result = response.json()

        return result.get("message", {}).get("content", "").strip()

    except requests.RequestException as error:
        raise ConnectionError(
            f"Ollama chat generation failed: {error}"
        ) from error
