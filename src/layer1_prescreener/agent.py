from pathlib import Path

from shared.context import load_core_rules
from shared.llm_client import call_llm

PROMPT_PATH = (
    Path(__file__).parent.parent.parent / "prompts" / "agents" / "01_prescreener.md"
)


def _load_prompt(ticker: str) -> str:
    template = PROMPT_PATH.read_text(encoding="utf-8")
    return template.replace("{{ CORE_RULES }}", load_core_rules()).replace(
        "[TICKER]", ticker
    )


def run_prescreener(ticker: str) -> dict:
    prompt = _load_prompt(ticker)
    result = call_llm(prompt)
    result["ticker"] = ticker
    return result
