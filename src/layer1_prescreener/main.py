from .agent import run_prescreener

PASSING_VERDICTS = {"PASS", "CONDITIONAL_PASS"}


def run_prescreener_batch(tickers: list[str]) -> list[dict]:
    results = []
    for ticker in tickers:
        result = run_prescreener(ticker)
        if result.get("verdict") in PASSING_VERDICTS:
            results.append(result)
    return results
