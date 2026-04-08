"""Prompt template loader for AI Insights service."""

import os
from functools import lru_cache

PROMPT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "prompts")


@lru_cache()
def load_prompt(name: str) -> str:
    """Load a prompt template from the prompts directory.

    Args:
        name: Prompt file name (without .txt extension).

    Returns:
        The prompt template string.
    """
    path = os.path.join(PROMPT_DIR, f"{name}.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def get_coaching_prompt() -> str:
    return load_prompt("coaching_prompt")


def get_session_review_prompt() -> str:
    return load_prompt("session_review_prompt")


def get_daily_briefing_prompt() -> str:
    return load_prompt("daily_briefing_prompt")


def get_pattern_discovery_prompt() -> str:
    return load_prompt("pattern_discovery_prompt")
