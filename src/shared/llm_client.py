import json
import logging

import anthropic
import httpx
from json_repair import repair_json

from shared.config_loader import get_llm_config

logger = logging.getLogger(__name__)

_CLAUDE_MODEL = "claude-sonnet-4-6"


def _call_claude(prompt: str, cfg: dict) -> str:
    client = anthropic.Anthropic(api_key=cfg["anthropic_api_key"])
    message = client.messages.create(
        model=_CLAUDE_MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def _call_ollama(prompt: str, cfg: dict) -> str:
    response = httpx.post(
        f"{cfg['ollama_base_url']}/api/generate",
        json={"model": cfg["ollama_model"], "prompt": prompt, "stream": False},
        timeout=1800.0,
    )
    response.raise_for_status()
    return response.json()["response"]


def _safe_parse_json(response: str) -> dict:
    if not response or not response.strip():
        raise ValueError("Model zwrócił pustą odpowiedź")
    response = response.strip()

    try:
        result = json.loads(response)
        if isinstance(result, dict):
            return result
    except json.JSONDecodeError:
        pass

    start = response.find("{")
    end = response.rfind("}")

    if start != -1 and end != -1 and end > start:
        try:
            result = json.loads(response[start : end + 1])
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError:
            pass

    if start != -1:
        try:
            result = json.loads(repair_json(response[start:]))
            if isinstance(result, dict):
                return result
        except json.JSONDecodeError, ValueError:
            pass

    logger.error(f"JSON parse failed: {response[:200]}")
    raise ValueError(f"Brak JSON w odpowiedzi: {response[:200]}")


def call_llm(prompt: str, expect_json: bool = True) -> str | dict:
    cfg = get_llm_config()
    logger.debug(f"Prompt:\n{prompt}")
    raw = _call_claude(prompt, cfg) if cfg["use_claude"] else _call_ollama(prompt, cfg)
    logger.debug(f"Raw response:\n{raw}")
    if expect_json:
        return _safe_parse_json(raw)
    return raw
