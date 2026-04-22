import logging
from pathlib import Path

from shared.context import load_core_rules
from shared.llm_client import call_llm
from shared.logging_config import log_agent_result
from shared.market_data import get_financial_context, get_price_context

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts" / "agents"


def _load_prompt(
    filename: str, ticker: str, price_context: str = "", financial_context: str = ""
) -> str:
    template = (PROMPTS_DIR / filename).read_text(encoding="utf-8")
    return (
        template.replace("{{ CORE_RULES }}", load_core_rules())
        .replace("[TICKER]", ticker)
        .replace("{{ PRICE_CONTEXT }}", price_context)
        .replace("{{ FINANCIAL_CONTEXT }}", financial_context)
    )


def run_fundamental(ticker: str) -> dict:
    fin_ctx = get_financial_context(ticker)
    result = call_llm(
        _load_prompt("02a_fundamental.md", ticker, financial_context=fin_ctx)
    )
    result["ticker"] = ticker
    log_agent_result(ticker, "fundamental", result)
    return result


def run_technical(ticker: str) -> dict:
    price_ctx = get_price_context(ticker)
    result = call_llm(_load_prompt("02b_technical.md", ticker, price_ctx))
    result["ticker"] = ticker
    log_agent_result(ticker, "technical", result)
    return result


def run_sentiment(ticker: str) -> dict:
    result = call_llm(_load_prompt("02c_sentiment.md", ticker))
    result["ticker"] = ticker
    log_agent_result(ticker, "sentiment", result)
    return result


def run_ownership(ticker: str) -> dict:
    fin_ctx = get_financial_context(ticker)
    result = call_llm(
        _load_prompt("02d_ownership.md", ticker, financial_context=fin_ctx)
    )
    result["ticker"] = ticker
    log_agent_result(ticker, "ownership", result)
    return result
