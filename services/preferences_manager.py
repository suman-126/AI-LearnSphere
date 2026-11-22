import json
import os

from config.settings import (
    DEFAULT_LANGUAGE,
    DEFAULT_LEARNING_LEVEL,
    DEFAULT_EXPLANATION_STYLE,
    DEFAULT_LLM_MODEL,
    DEFAULT_THEME,
    SUPPORTED_LANGUAGES,
    LEARNING_LEVELS,
    EXPLANATION_STYLES,
    SUPPORTED_THEMES
)


SETTINGS_FILE = os.path.join(
    "data",
    "user_settings.json"
)


def get_default_preferences():
    """Return the application's default user preferences."""

    return {
        "language": DEFAULT_LANGUAGE,
        "learning_level": DEFAULT_LEARNING_LEVEL,
        "explanation_style": DEFAULT_EXPLANATION_STYLE,
        "model": DEFAULT_LLM_MODEL,
        "theme": DEFAULT_THEME
    }


def load_preferences():
    """Load saved preferences or return default preferences."""

    defaults = get_default_preferences()

    try:
        if not os.path.exists(SETTINGS_FILE):
            return defaults

        with open(SETTINGS_FILE, "r", encoding="utf-8") as file:
            saved_preferences = json.load(file)

        if not isinstance(saved_preferences, dict):
            return defaults

        preferences = defaults.copy()
        preferences.update(saved_preferences)

        if preferences["language"] not in SUPPORTED_LANGUAGES:
            preferences["language"] = DEFAULT_LANGUAGE

        if preferences["learning_level"] not in LEARNING_LEVELS:
            preferences["learning_level"] = DEFAULT_LEARNING_LEVEL

        if preferences["explanation_style"] not in EXPLANATION_STYLES:
            preferences["explanation_style"] = DEFAULT_EXPLANATION_STYLE

        if preferences["theme"] not in SUPPORTED_THEMES:
            preferences["theme"] = DEFAULT_THEME

        if not isinstance(preferences["model"], str) or not preferences["model"].strip():
            preferences["model"] = DEFAULT_LLM_MODEL

        return preferences

    except (OSError, json.JSONDecodeError):
        return defaults


def save_preferences(preferences):
    """Save user preferences to a local JSON file."""

    if not isinstance(preferences, dict):
        raise ValueError("Preferences must be a dictionary.")

    os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)

    with open(SETTINGS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            preferences,
            file,
            indent=4,
            ensure_ascii=False
        )


def reset_preferences():
    """Restore and save the default preferences."""

    defaults = get_default_preferences()

    save_preferences(defaults)

    return defaults
