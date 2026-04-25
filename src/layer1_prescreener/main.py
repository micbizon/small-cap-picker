import logging

from .agent import run_prescreener

logger = logging.getLogger(__name__)

PASSING_VERDICTS = {"PASS", "CONDITIONAL_PASS"}


def run_prescreener_batch(tickers: list[str]) -> list[dict]:
    results = []
    for ticker in tickers:
        try:
            result = run_prescreener(ticker)
        except Exception as e:
            logger.warning(
                f"[prescreener] {ticker}: błąd parsowania — traktuję jako REJECT ({e})"
            )
            continue
        verdict = result.get("verdict", "UNKNOWN")
        logger.info(f"[prescreener] {ticker}: {verdict}")
        if verdict in PASSING_VERDICTS:
            results.append(result)
    passed = len(results)
    logger.info(f"[prescreener] {passed}/{len(tickers)} tickerów przeszło filtr")
    return results
