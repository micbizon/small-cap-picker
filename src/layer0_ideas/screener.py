import logging

from finvizfinance.screener.overview import Overview

logger = logging.getLogger(__name__)

_FILTERS = {
    "Market Cap.": "Small ($300mln to $2bln)",
    "Sales growthqtr over qtr": "Over 15%",
    "InsiderOwnership": "Over 10%",
}


def fetch_screener_candidates() -> list[str]:
    try:
        overview = Overview()
        overview.set_filter(filters_dict=_FILTERS)
        df = overview.screener_view()
    except Exception as e:
        logger.error("Finviz screener failed: %s", e)
        return []

    if df is None or df.empty:
        logger.warning("screener: Finviz returned empty result")
        return []

    tickers = df["Ticker"].dropna().str.strip().str.upper().tolist()
    logger.info("screener: found %d candidates", len(tickers))
    return tickers
