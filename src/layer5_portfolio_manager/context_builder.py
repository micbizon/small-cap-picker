import json

from shared.config_loader import (
    load_decisions_log,
    load_portfolio,
    load_system_insights,
)
from shared.context import load_core_rules


def _portfolio_state_section(portfolio: dict) -> str:
    positions = portfolio.get("positions", [])
    cash_pct = portfolio.get("cash_pct", 0)
    tickers_line = ", ".join(p["ticker"] for p in positions) if positions else "brak"
    lines = [
        f"Aktualne pozycje: {tickers_line}",
        f"Dostępna gotówka: {cash_pct}%",
        "Przy decyzji BUY lub SWAP uwzględnij dostępną gotówkę.",
    ]
    return "\n".join(lines)


def build_context(ticker: str, layer2: dict, layer4: dict) -> str:
    decisions_with_feedback = [
        d
        for d in load_decisions_log()
        if d.get("feedback_6m") is not None or d.get("feedback_12m") is not None
    ]
    decisions_with_feedback.sort(key=lambda d: d.get("date", ""), reverse=True)
    recent_feedback = decisions_with_feedback[:10]

    portfolio = load_portfolio()

    sections = [
        ("CORE INVESTMENT RULES", load_core_rules()),
        (
            "CURRENT PORTFOLIO",
            json.dumps(portfolio, ensure_ascii=False, indent=2),
        ),
        ("STAN PORTFELA", _portfolio_state_section(portfolio)),
        (
            "PAST DECISIONS WITH FEEDBACK (newest first, max 10)",
            json.dumps(recent_feedback, ensure_ascii=False, indent=2),
        ),
        (
            "SYSTEM INSIGHTS (agent accuracy & known bias patterns)",
            json.dumps(load_system_insights(), ensure_ascii=False, indent=2),
        ),
        (
            f"LAYER 2 ANALYSIS FOR {ticker}",
            json.dumps(layer2, ensure_ascii=False, indent=2),
        ),
        (
            f"LAYER 4 CASES FOR {ticker} (bull / bear / pre-mortem)",
            json.dumps(layer4, ensure_ascii=False, indent=2),
        ),
    ]

    return "\n\n".join(f"## {title}\n{content}" for title, content in sections)
