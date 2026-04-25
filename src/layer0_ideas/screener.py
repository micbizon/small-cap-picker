import logging

from finvizfinance.screener.overview import Overview

logger = logging.getLogger(__name__)

_FILTERS = {
    "Market Cap.": "Small to Large ($1bln to $100bln)",
    "Sales growthqtr over qtr": "Over 15%",
    "InsiderOwnership": "Over 10%",
}


def fetch_screener_candidates() -> list[str]:
    try:
        overview = Overview()
        overview.set_filter(filters_dict=_FILTERS)
        df = overview.screener_view()
    except Exception as e:
        logger.error(f"Finviz screener failed: {e}")
        return []

    if df is None or df.empty:
        logger.warning("screener: Finviz returned empty result")
        return []

    tickers = df["Ticker"].dropna().str.strip().str.upper().tolist()
    logger.info(f"screener: found {len(tickers)} candidates")
    return tickers
