# Changelog

## 2026-04-19 — TASK-015: Centralizacja MAX_WORKERS przez zmienną środowiskową

Dodano `get_max_workers()` do `config_loader.py` — czyta `MAX_WORKERS` z `.env`, domyślnie `4`. We wszystkich trzech miejscach z hardkodowanymi wartościami (`layer2_analysis/main.py` → 4, `layer4_cases/main.py` → 3, `pipeline/orchestrator.py` → 8×2) zastąpiono stałe wywołaniem `get_max_workers()` (w orchestratorze jako `min(len(tickers), get_max_workers())`). Dodano `MAX_WORKERS=` do `.env.example`.

---

## 2026-04-19 — TASK-014: Naprawa parsowania JSON i retry w warstwie 2 i 4

`_safe_parse_json` w `llm_client.py` przepisany na 4-krokowy fallback: `json.loads(response)` → `json.loads(response[start:end+1])` → `repair_json(response[start:])` (krok c obsługuje ucięty JSON bez zamykającego `}`) → `ValueError`. W `orchestrator.py` naprawiony retry w warstwie 2 i 4: zamiast `_call_with_retry(future.result)` (odczytywał zapamiętany wyjątek z zakończonego future) retry przeniesiony do workerów jako `ex.submit(_call_with_retry, run_parallel_analysis, t)` — równoległość między tickerami zachowana, ponowienie wywołuje agenta od nowa.

---

## 2026-04-19 — TASK-013: Integracja portfolio.yaml z pipeline

W `orchestrator.py` force-add wszystkich tickerów z `portfolio_tickers` do pipelinu przed podziałem na `non_portfolio`/`in_portfolio` — tickery spoza watchlist trafiają teraz zawsze do warstwy 2+. W `layer3_selector/main.py` dodano `print` warning gdy `weighted_score < MIN_SCORE_THRESHOLD` dla spółki z portfolio — sygnał psującej się tezy. W `context_builder.py` wyodrębniono `_portfolio_state_section()` która buduje czytelną sekcję "STAN PORTFELA" z listą tickerów i `cash_pct`, z dodatkową linią ostrzegawczą gdy `cash_pct < 5%`.

---

## 2026-04-19 — TASK-012: Usunięcie calculate_recommended_size

Usunięto `position_sizing.py` w całości. Z `context_builder.py` usunięto import, wywołanie `calculate_recommended_size()` oraz sekcję "RECOMMENDED POSITION SIZE" z kontekstu budowanego dla agenta. Z `_build_decision_payload()` w `main.py` usunięto pola `recommended_position_size_pct` i `sizing_override_reason`. Z JSON output w `05_portfolio_manager.md` usunięto te same dwa pola. Z `decisions_log.yaml` usunięto te pola z wpisu DEC-001.

---

## 2026-04-18 — TASK-011: Naprawa źródeł danych w warstwie 0

`fetch_insider_buys()` w `insider_buying.py` zastąpiony stubem zwracającym `[]` z `logger.warning` — OpenInsider niedostępny ze środowiska. `screener.py` przepisany na `finvizfinance.screener.overview.Overview` z filtrami `Market Cap.: Small`, `Sales growthqtr over qtr: Over 15%`, `InsiderOwnership: Over 10%` — poprawne nazwy filtrów ustalone empirycznie (Finviz używa `InsiderOwnership` bez spacji). `aggregator.py` loguje info gdy tylko jedno źródło aktywne. Wynik: 227 tickerów dodanych do watchlist.yaml.

---


## 2026-04-18 — TASK-010: Wyodrębnienie call_llm do współdzielonego modułu

Stworzono `/src/shared/llm_client.py` z funkcjami `_call_claude`, `_call_ollama`, `_safe_parse_json` (json.loads → repair_json → ValueError) i publicznym `call_llm(prompt, expect_json=True)` który wybiera backend z `get_llm_config()`. Usunięto lokalne implementacje z warstw 1, 2, 4, 5 i 6 — każdy agent importuje teraz tylko `call_llm`. Grep na `ollama_base_url` zwraca wyłącznie `llm_client.py` i `config_loader.py`.

---


## 2026-04-18 — TASK-009: Warstwa 0 — Idea Generation (automatyczny watchlist)

`fetch_insider_buys()` w `insider_buying.py` pobiera CSV z OpenInsider przez `httpx`, filtruje transakcje typu P dla ról CEO/CFO/Director z wartością ≥ $100K i weryfikuje market cap $100M–$25B przez `yfinance.fast_info`. `fetch_screener_candidates()` w `screener.py` pobiera CSV z Finviz export z filtrami `cap_small,cap_mid,iown_o10`, następnie weryfikuje revenue growth YoY ≥ 15% przez `yfinance.financials`. `run_idea_generation()` w `aggregator.py` łączy oba źródła, deduplikuje względem istniejących wpisów w watchlist.yaml i dopisuje nowe jako `{ticker, source, discovery_date}` — format zgodny z `t["ticker"]` używanym przez orchestrator. Dodano `yfinance` do zależności przez `uv add`.

---


## 2026-04-18 — TASK-008: Pipeline — Orchestrator łączący wszystkie warstwy

`run_pipeline()` w `orchestrator.py` łączy warstwy 1–5 w jeden spójny przepływ: ticki portfolio omijają warstwę 1, warstwy 2 i 4 wykonywane są równolegle między tickerami (`ThreadPoolExecutor`), warstwa 5 ograniczona do top 5 + portfolio żeby kontrolować koszt Claude API. `main.py` jako punkt wejścia CLI obsługuje `--tickers`, `--feedback` i tryb domyślny z `watchlist.yaml`.

---

## 2026-04-18 — TASK-007: Warstwa 6 — Feedback Loop Agent

Stworzono agenta warstwy 6: `feedback_agent.py` ładuje prompt z `feedback_loop.md`, podstawia `[DECISION]`, `[CURRENT_DATA]`, `[MONTHS]` i wywołuje LLM (Claude API lub Ollama w zależności od `USE_CLAUDE_API`). `insights_updater.py` aktualizuje liczniki `agent_accuracy` w `system_insights.yaml` i dodaje `recurring_pattern` bez duplikatów. `main.py` skanuje `decisions_log.yaml` i wypełnia `feedback_6m`/`feedback_12m` dla decyzji starszych niż 6/12 miesięcy.

---

## 2026-04-17 — TASK-006: Warstwa 5 — Portfolio Manager Agent

Stworzono agenta warstwy 5 opartego na Claude API: `context_builder` składa pełny kontekst z 7 sekcji (CORE_RULES, portfolio, feedback, system_insights, wyniki L2/L4, recommended size), `main.py` wywołuje `claude-sonnet-4-6` i zapisuje decyzję do `decisions_log.yaml` przez `save_decision()`.

---

## 2026-04-17 — TASK-005: Warstwa 4 — Bull, Bear i Pre-Mortem agenty

Stworzono 3 prompty i agenty warstwy 4 uruchamiane równolegle; pre-mortem podstawia rok `now+2` jako `[FUTURE_YEAR]`, wszystkie trzy dostają kontekst z warstwy 2 jako JSON.

---

## 2026-04-17 — TASK-004: Warstwa 3 — Selektor i ranking

`run_selector()` agreguje wyniki 4 agentów warstwy 2 w weighted score i zwraca top 20 kandydatów; spółki z portfolio zawsze trafiają do outputu z flagą `in_portfolio: true` niezależnie od score'u.

---

## 2026-04-17 — TASK-003: Warstwa 2 — Cztery agenty analizy równoległej

Stworzono 4 prompty dla agentów warstwy 2 (fundamental, technical, sentiment, ownership) oraz `agents.py` z osobną funkcją dla każdego agenta. `main.py` uruchamia wszystkie cztery równolegle przez `ThreadPoolExecutor` — czas wykonania równy najwolniejszemu agentowi.

---

## 2026-04-17 — TASK-002: Warstwa 1 — Pre-screener agent

Stworzono agenta warstwy 1: `agent.py` ładuje prompt z pliku, podstawia CORE_RULES i ticker, wysyła do ollama i parsuje JSON z fallbackiem na regex. `main.py` uruchamia batch i filtruje tylko PASS/CONDITIONAL_PASS.

---

## 2026-04-17 — TASK-001: Infrastruktura bazowa

Stworzono shared utilities: `config_loader.py` (load/save YAML dla portfolio, watchlist, decisions_log, system_insights), `context.py` (load_core_rules z pliku), `logger.py` (save_decision z auto-incrementem DEC-NNN). Dodano pliki konfiguracyjne: `decisions_log.yaml`, `system_insights.yaml`, `portfolio.yaml`, `watchlist.yaml`.
