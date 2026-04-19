import json
from datetime import datetime
from pathlib import Path

from shared.context import load_core_rules
from shared.llm_client import call_llm
from shared.market_data import get_price_context

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts" / "agents"


def _load_prompt(
    filename: str,
    ticker: str,
    layer2_context: dict,
    extra: dict = None,
    price_context: str = "",
) -> str:
    template = (PROMPTS_DIR / filename).read_text(encoding="utf-8")
    prompt = (
        template.replace("{{ CORE_RULES }}", load_core_rules())
        .replace("[TICKER]", ticker)
        .replace(
            "[LAYER2_CONTEXT]", json.dumps(layer2_context, ensure_ascii=False, indent=2)
        )
        .replace("{{ PRICE_CONTEXT }}", price_context)
    )
    if extra:
        for key, value in extra.items():
            prompt = prompt.replace(key, str(value))
    return prompt


def run_bull(ticker: str, layer2_context: dict) -> dict:
    price_ctx = get_price_context(ticker)
    result = call_llm(_load_prompt("04a_bull.md", ticker, layer2_context, price_context=price_ctx))
    result["ticker"] = ticker
    return result


def run_bear(ticker: str, layer2_context: dict) -> dict:
    price_ctx = get_price_context(ticker)
    result = call_llm(_load_prompt("04b_bear.md", ticker, layer2_context, price_context=price_ctx))
    result["ticker"] = ticker
    return result


def run_premortem(ticker: str, layer2_context: dict) -> dict:
    future_year = datetime.now().year + 2
    prompt = _load_prompt(
        "04c_premortem.md", ticker, layer2_context, {"[FUTURE_YEAR]": future_year}
    )
    result = call_llm(prompt)
    result["ticker"] = ticker
    return result
