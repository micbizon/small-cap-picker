from shared.config_loader import run_agents_parallel

from .agents import run_bear, run_bull, run_premortem

_AGENTS = {
    "bull": run_bull,
    "bear": run_bear,
    "premortem": run_premortem,
}


def run_cases(ticker: str, layer2_context: dict) -> dict:
    return run_agents_parallel(_AGENTS, ticker, layer2_context)
