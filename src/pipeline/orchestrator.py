import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from layer1_prescreener.main import run_prescreener_batch
from layer2_analysis.main import run_parallel_analysis
from layer3_selector.main import run_selector
from layer4_cases.main import run_cases
from layer5_portfolio_manager.main import run_portfolio_manager
from shared.config_loader import get_max_workers, load_portfolio, load_watchlist

_TOP_N_FOR_PM = 5


def _log(step: str, entered: int, exited: int) -> None:
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {step}: wejście={entered}, wyjście={exited}")


def _call_with_retry(fn, *args, max_retries: int = None, **kwargs):
    if max_retries is None:
        max_retries = int(os.getenv("LLM_MAX_RETRIES", "3"))
    for attempt in range(1, max_retries + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            print(f"  Próba {attempt}/{max_retries} nieudana: {e}")
            if attempt == max_retries:
                raise


def run_pipeline(tickers: list[str] | None = None) -> None:
    if tickers is None:
        watchlist = load_watchlist()
        tickers = (
            [t["ticker"] for t in watchlist.get("tickers", [])]
            if isinstance(watchlist.get("tickers"), list)
            else []
        )

    portfolio = load_portfolio()
    portfolio_tickers = {p["ticker"] for p in portfolio.get("positions", [])}

    # Force-add all portfolio tickers regardless of watchlist
    extra = [t for t in portfolio_tickers if t not in tickers]
    if extra:
        print(
            f"Dodano {len(extra)} tickerów z portfolio do pipeline (bypass prescreener): {extra}"
        )
    all_tickers = list(dict.fromkeys(tickers + list(portfolio_tickers)))
    non_portfolio = [t for t in all_tickers if t not in portfolio_tickers]
    in_portfolio = [t for t in all_tickers if t in portfolio_tickers]

    # Layer 1 — only non-portfolio tickers
    print(f"\n--- Warstwa 1: Pre-screener ({len(non_portfolio)} tickerów) ---")
    passing = run_prescreener_batch(non_portfolio)
    passing_tickers = [r["ticker"] for r in passing]
    _log("L1 prescreener", len(non_portfolio), len(passing_tickers))

    # Layer 2 — passing + portfolio (always)
    layer2_tickers = list(dict.fromkeys(passing_tickers + in_portfolio))
    print(f"\n--- Warstwa 2: Analiza równoległa ({len(layer2_tickers)} tickerów) ---")

    layer2_results: dict[str, dict] = {}
    with ThreadPoolExecutor(
        max_workers=min(len(layer2_tickers), get_max_workers())
    ) as ex:
        futures = {
            ex.submit(_call_with_retry, run_parallel_analysis, t): t
            for t in layer2_tickers
        }
        for future in as_completed(futures):
            ticker = futures[future]
            layer2_results[ticker] = future.result()
    _log("L2 analiza", len(layer2_tickers), len(layer2_results))

    # Layer 3 — selector
    print("\n--- Warstwa 3: Selektor ---")
    analyses = list(layer2_results.values())
    selected = run_selector(analyses)
    _log("L3 selektor", len(analyses), len(selected))

    # Layer 4 — bull/bear/premortem for all selected, parallel across tickers
    print(f"\n--- Warstwa 4: Bull/Bear/Pre-Mortem ({len(selected)} tickerów) ---")
    layer4_results: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=min(len(selected), get_max_workers())) as ex:
        futures = {
            ex.submit(
                _call_with_retry, run_cases, entry["ticker"], entry["analysis"]
            ): entry["ticker"]
            for entry in selected
        }
        for future in as_completed(futures):
            ticker = futures[future]
            layer4_results[ticker] = future.result()
    _log("L4 cases", len(selected), len(layer4_results))

    # Layer 5 — top 5 non-portfolio + all portfolio tickers
    top5_tickers = [e["ticker"] for e in selected if not e["in_portfolio"]][
        :_TOP_N_FOR_PM
    ]
    pm_tickers = list(dict.fromkeys(top5_tickers + in_portfolio))

    print(f"\n--- Warstwa 5: Portfolio Manager ({len(pm_tickers)} tickerów) ---")
    for ticker in pm_tickers:
        l2 = layer2_results.get(ticker, {})
        l4 = layer4_results.get(ticker, {})
        try:
            result = _call_with_retry(run_portfolio_manager, ticker, l2, l4)
            print(
                f"  {ticker}: {result.get('action', '?')} ({result.get('position_size_pct', '?')}%)"
            )
        except ValueError as e:
            print(f"  {ticker}: BŁĄD parsowania JSON — pomijam ({e})")
            continue
        except Exception as e:
            print(f"  {ticker}: NIEOCZEKIWANY BŁĄD — pomijam ({e})")
            continue
    _log("L5 portfolio manager", len(pm_tickers), len(pm_tickers))

    print("\n--- Pipeline zakończony ---")
