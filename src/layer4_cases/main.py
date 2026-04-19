from concurrent.futures import ThreadPoolExecutor, as_completed

from shared.config_loader import get_max_workers

from .agents import run_bear, run_bull, run_premortem

_AGENTS = {
    "bull": run_bull,
    "bear": run_bear,
    "premortem": run_premortem,
}


def run_cases(ticker: str, layer2_context: dict) -> dict:
    results = {}
    with ThreadPoolExecutor(max_workers=get_max_workers()) as executor:
        futures = {
            executor.submit(fn, ticker, layer2_context): name
            for name, fn in _AGENTS.items()
        }
        for future in as_completed(futures):
            name = futures[future]
            results[name] = future.result()
    return results
