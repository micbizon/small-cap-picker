from shared.config_loader import run_agents_parallel

from .agents import run_fundamental, run_ownership, run_sentiment, run_technical

_AGENTS = {
    "fundamental": run_fundamental,
    "technical": run_technical,
    "sentiment": run_sentiment,
    "ownership": run_ownership,
}


def run_parallel_analysis(ticker: str) -> dict:
    return run_agents_parallel(_AGENTS, ticker)
