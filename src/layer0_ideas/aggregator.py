import logging
from datetime import date
from pathlib import Path

import yaml

from layer0_ideas.insider_buying import fetch_insider_buys
from layer0_ideas.screener import fetch_screener_candidates

logger = logging.getLogger(__name__)

_WATCHLIST_PATH = Path(__file__).parent.parent.parent / "config" / "watchlist.yaml"


def _load_watchlist() -> dict:
    if not _WATCHLIST_PATH.exists():
        return {"tickers": []}
    with open(_WATCHLIST_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if "tickers" not in data:
        data["tickers"] = []
    return data


def _save_watchlist(data: dict) -> None:
    with open(_WATCHLIST_PATH, "w", encoding="utf-8") as f:
        yaml.dump(
            data, f, allow_unicode=True, default_flow_style=False, sort_keys=False
        )


def run_idea_generation() -> None:
    watchlist = _load_watchlist()
    existing = {
        entry["ticker"] for entry in watchlist["tickers"] if isinstance(entry, dict)
    }

    insider_tickers = fetch_insider_buys()
    if not insider_tickers:
        logger.info(
            "idea_generation: insider_buying niedostępny — używam tylko screener"
        )
    screener_tickers = fetch_screener_candidates()

    today = date.today().isoformat()
    added = 0

    for ticker in insider_tickers:
        if ticker not in existing:
            watchlist["tickers"].append(
                {"ticker": ticker, "source": "insider_buying", "discovery_date": today}
            )
            existing.add(ticker)
            added += 1

    for ticker in screener_tickers:
        if ticker not in existing:
            watchlist["tickers"].append(
                {"ticker": ticker, "source": "screener", "discovery_date": today}
            )
            existing.add(ticker)
            added += 1

    _save_watchlist(watchlist)
    logger.info("idea_generation: added %d new tickers to watchlist", added)
