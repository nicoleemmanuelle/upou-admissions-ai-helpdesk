"""OpenAI service wrapper used by the Lambda handler.

This file uses the OpenAI Python client. The environment variable OPENAI_API_KEY
must be set in the Lambda function configuration.
"""

import os
import json
import logging
from typing import Optional
from urllib import request, error

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))


def _load_system_prompt() -> str:
    prompt_path = os.path.join(os.path.dirname(__file__), "prompt.txt")
    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        logger.warning("prompt.txt not found; using a minimal default prompt")
        return (
            "You are a helpful and factual UPOU admissions helpdesk assistant. "
            "Only answer using information provided in the context. If the answer is not in the context, say you don't know."
        )


def ask_openai(user_query: str, context: str, model: Optional[str] = None) -> str:
    """Call the OpenAI HTTP API directly using urllib (no external deps).

    This implements a minimal Chat Completions-style request using the newer
    OpenAI chat completions endpoint. It's intentionally minimal: production
    code should use retry/backoff and better error handling.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is required")

    model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    system_prompt = _load_system_prompt()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{user_query}"},
    ]

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "max_tokens": 800,
        "temperature": 0.0,
    }).encode("utf-8")

    req = request.Request(
        url="https://api.openai.com/v1/chat/completions",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body)
    except error.HTTPError as e:
        logger.exception("OpenAI HTTP error: %s", e)
        raise
    except Exception:
        logger.exception("Unexpected error calling OpenAI")
        raise

    choices = data.get("choices") or []
    if not choices:
        return ""

    message = choices[0].get("message") or {}
    return message.get("content", "").strip()