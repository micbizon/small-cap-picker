import logging
from pathlib import Path

from shared.context import load_core_rules, read_template
from shared.llm_client import call_llm
from shared.logging_config import log_agent_result

logger = logging.getLogger(__name__)

PROMPT_PATH = (
    Path(__file__).parent.parent.parent / "prompts" / "agents" / "01_prescreener.md"
)


def _load_prompt(ticker: str) -> str:
    return (
        read_template(PROMPT_PATH)
        .replace("{{ CORE_RULES }}", load_core_rules())
        .replace("[TICKER]", ticker)
    )


def run_prescreener(ticker: str) -> dict:
    prompt = _load_prompt(ticker)
    logger.debug(f"[prescreener] {ticker} prompt:\n{prompt}")
    result = call_llm(prompt)
    result["ticker"] = ticker
    log_agent_result(ticker, "prescreener", result)
    return result
