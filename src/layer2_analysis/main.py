from concurrent.futures import ThreadPoolExecutor, as_completed

from .agents import run_fundamental, run_ownership, run_sentiment, run_technical

_AGENTS = {
    "fundamental": run_fundamental,
    "technical": run_technical,
    "sentiment": run_sentiment,
    "ownership": run_ownership,
}


def run_parallel_analysis(ticker: str) -> dict:
    results = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(fn, ticker): name for name, fn in _AGENTS.items()}
        for future in as_completed(futures):
            name = futures[future]
            results[name] = future.result()
    return results
