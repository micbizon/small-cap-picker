from pathlib import Path

from shared.context import load_core_rules
from shared.llm_client import call_llm
from shared.market_data import get_price_context

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts" / "agents"


def _load_prompt(filename: str, ticker: str, price_context: str = "") -> str:
    template = (PROMPTS_DIR / filename).read_text(encoding="utf-8")
    return (
        template.replace("{{ CORE_RULES }}", load_core_rules())
        .replace("[TICKER]", ticker)
        .replace("{{ PRICE_CONTEXT }}", price_context)
    )


def run_fundamental(ticker: str) -> dict:
    result = call_llm(_load_prompt("02a_fundamental.md", ticker))
    result["ticker"] = ticker
    return result


def run_technical(ticker: str) -> dict:
    price_ctx = get_price_context(ticker)
    result = call_llm(_load_prompt("02b_technical.md", ticker, price_ctx))
    result["ticker"] = ticker
    return result


def run_sentiment(ticker: str) -> dict:
    result = call_llm(_load_prompt("02c_sentiment.md", ticker))
    result["ticker"] = ticker
    return result


def run_ownership(ticker: str) -> dict:
    result = call_llm(_load_prompt("02d_ownership.md", ticker))
    result["ticker"] = ticker
    return result
