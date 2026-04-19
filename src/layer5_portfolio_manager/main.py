from datetime import date
from pathlib import Path

from shared.llm_client import call_llm
from shared.logger import save_decision

from .context_builder import build_context

PROMPT_PATH = (
    Path(__file__).parent.parent.parent
    / "prompts"
    / "agents"
    / "05_portfolio_manager.md"
)


def _build_decision_payload(
    ticker: str, pm_result: dict, layer2: dict, layer4: dict
) -> dict:
    l2_scores = {
        agent: layer2.get(agent, {}).get("score", 0)
        for agent in ("fundamental", "technical", "sentiment", "ownership")
    }
    l2_scores["bull"] = layer4.get("bull", {}).get("score", 0)
    l2_scores["bear"] = layer4.get("bear", {}).get("score", 0)

    scenarios = layer4.get("premortem", {}).get("failure_scenarios", [])
    top_risk = (
        scenarios[0].get("description", "")
        if scenarios
        else layer4.get("premortem", {}).get("top_blind_spot", "")
    )

    return {
        "ticker": ticker,
        "action": pm_result.get("action", ""),
        "position_size_pct": pm_result.get("position_size_pct", 0),
        "entry_price": 0.0,
        "entry_price_currency": "USD",
        "core_thesis": pm_result.get("core_thesis", ""),
        "key_assumptions": pm_result.get("key_assumptions", []),
        "stop_loss_price": pm_result.get("stop_loss_price", 0.0),
        "stop_loss_fundamental": pm_result.get("stop_loss_fundamental", ""),
        "checkin_1yr_criteria": pm_result.get("checkin_1yr_criteria", ""),
        "scores": l2_scores,
        "premortem_top_risk": top_risk,
        "feedback_6m": None,
        "feedback_12m": None,
    }


def run_portfolio_manager(ticker: str, layer2: dict, layer4: dict) -> dict:
    context = build_context(ticker, layer2, layer4)
    print(f"CONTEXT PREVIEW:\n{context}\n\n")
    template = PROMPT_PATH.read_text(encoding="utf-8")
    prompt = template.replace("{{ FULL_CONTEXT }}", context)

    pm_result = call_llm(prompt)
    pm_result["ticker"] = ticker

    payload = _build_decision_payload(ticker, pm_result, layer2, layer4)
    payload["date"] = str(date.today())
    save_decision(payload)

    return pm_result
