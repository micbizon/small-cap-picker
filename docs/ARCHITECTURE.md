# Multi-Agent Investment System — Architecture

## Cel systemu

System automatycznej selekcji spółek small/mid-cap (głównie USA, opcjonalnie PL) z przewagą
wynikającą z małej kapitalizacji — obszaru gdzie duże fundusze instytucjonalne nie mogą efektywnie
operować. Decyzje inwestycyjne oparte o framework "Costco Algorithm": spółki z flywheel'em
reinwestującym korzyści skali w niższe ceny / wyższą wartość dla klienta końcowego.

**Zakres kapitalizacji:** $100M – $25B (small/mid-cap)  
**Horyzont inwestycyjny:** 3–10 lat per pozycja  
**Liczba pozycji:** 3–7 jednocześnie  
**Filozofia:** concentrated, high-conviction, long-only

---

## Filozofia inwestycyjna (Costco Algorithm)

Spółka przechodzi przez system tylko jeśli posiada strukturalne cechy flywheel'u:

1. **Economies of scale shared** — wzrost skali → niższe koszty jednostkowe → niższe ceny lub
   wyższa wartość dla klienta → więcej klientów → wzrost skali (pętla zamknięta)
2. **Goodwill compounding** — długoterminowe budowanie lojalności klientów jako niemierzalny, ale
   realny aktyw
3. **Reinvestment over margin expansion** — preferencja dla spółek które reinwestują zyski w
   produkt/cenę zamiast optymalizować krótkoterminowy EPS
4. **Asymmetric upside** — teza musi mieć potencjał 3–10x w horyzoncie 5–7 lat przy zdefiniowanym
   ryzyku downside

---

## Stack technologiczny

Środowisko systemu jest w całości zarządzane poprzez narzędzie `uv`.

---

## Architektura systemu — warstwy

```
┌─────────────────────────────────────────────────────────┐
│  WARSTWA 0: Idea Generation                             │
│  Źródła: screeners, 13F małych funduszy, insider buying │
│  Output: lista TICKER-ów do analizy                     │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│  WARSTWA 1: Pre-Screener (Costco Algorithm Filter)      │
│  Model: lokalny LLM (Llama 70B)                         │
│  Prompt: /prompts/agents/01_prescreener.md              │
│  Output: PASS / CONDITIONAL PASS / REJECT               │
│  Eliminuje ~70-80% kandydatów tanio (mało tokenów)      │
└─────────────────────┬───────────────────────────────────┘
                      │ (tylko PASS i CONDITIONAL PASS)
┌─────────────────────▼───────────────────────────────────┐
│  WARSTWA 2: Równoległa analiza (4 agenty)               │
│                                                         │
│  ┌───────────────┐  ┌──────────────┐                    │
│  │ 2A Fundamental│  │ 2B Technical │                    │
│  │ Llama 70B     │  │ Llama 70B    │                    │
│  └───────────────┘  └──────────────┘                    │
│  ┌───────────────┐  ┌──────────────┐                    │
│  │ 2C Sentiment  │  │ 2D Ownership │ ← nowy agent       │
│  │ Llama 70B     │  │ Llama 70B    │                    │
│  └───────────────┘  └──────────────┘                    │
│                                                         │
│  Każdy agent zwraca: { score: 1-10, verdict, summary }  │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│  WARSTWA 3: Selekcja Top 10–20                          │
│  Ranking weighted score z warstwy 2                     │
│  Wagi: Fundamental 40%, Technical 20%,                  │
│        Sentiment 25%, Ownership 15%                     │
│  + Spółki aktualnie w portfolio (zawsze przechodzą)     │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│  WARSTWA 4: Bull / Bear / Pre-Mortem (3 agenty)         │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │ 4A Bull Case │  │ 4B Bear Case │  │ 4C Pre-Mortem │  │
│  │ Llama 70B    │  │ Llama 70B    │  │ Llama 70B     │  │
│  └──────────────┘  └──────────────┘  └───────────────┘  │
│                                                         │
│  Pre-Mortem: zakłada -65% za 2 lata i odtwarza przyczynę│
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│  WARSTWA 5: Portfolio Manager Agent                     │
│  Model: Claude API (claude-sonnet)                      │
│  Prompt: /prompts/agents/05_portfolio_manager.md        │
│  Kontekst: portfolio.json + decisions_log.json          │
│                                                         │
│  Decyzje: BUY / ADD / HOLD / SWAP / PASS                │
│  Output: decyzja + teza + założenia + stop-loss         │
│  → Zapisuje do decisions_log.json                       │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│  WARSTWA 6: Feedback Loop (uruchamiany co 6/12 miesięcy)│
│  Model: Claude API                                      │
│  Prompt: /prompts/system/feedback_loop.md               │
│  Wejście: decisions_log.json (decyzje starsze niż 6 msc)│
│  Output: ocena założeń, które się sprawdziły, które nie │
│  → Uczy system rozpoznawać własne błędy                 │
└─────────────────────────────────────────────────────────┘
```

---

## Struktura plików projektu

```
/investment-agent
│
├── /docs
│   ├── ARCHITECTURE.md        ← ten plik
│   ├── PHILOSOPHY.md          ← Costco Algorithm szczegółowo
│
├── /prompts
│   ├── /agents
│   │   ├── 01_prescreener.md
│   │   ├── 02a_fundamental.md
│   │   ├── 02b_technical.md
│   │   ├── 02c_sentiment.md
│   │   ├── 02d_ownership.md
│   │   ├── 04a_bull.md
│   │   ├── 04b_bear.md
│   │   ├── 04c_premortem.md
│   │   └── 05_portfolio_manager.md
│   └── /system
│       ├── idea_generation.md
│       └── feedback_loop.md
│
├── /config
│   ├── portfolio.yaml         ← aktualne pozycje i ceny wejścia
│   ├── watchlist.yaml         ← spółki do obserwacji
│   └── decisions_log.json     ← pełna historia decyzji z tezami
│
├── /src                       ← kod (osobna sprawa)
│
├── .env                       ← zmienne środowiskowe, np nazwa modelu
├── TASKS.md                   ← kolejka zadań do implementacji
└── CHANGELOG.md               ← historia zmian systemu
└── README.md
```

---

## Modele LLM — podział odpowiedzialności

Do implementacji używamy tylko i wyłącznie modelu **llama3.2:3b**

| Warstwa | Agent | Model | Uzasadnienie |
|---------|-------|-------|--------------|
| 1 | Pre-screener | Llama 70B (lokalny) | Prosty filtr tak/nie, duży wolumen, tani |
| 2A | Fundamental | Llama 70B (lokalny) | Ustrukturyzowana analiza, powtarzalny format |
| 2B | Technical | Llama 70B (lokalny) | Dane liczbowe, mało interpretacji jakościowej |
| 2C | Sentiment | Llama 70B (lokalny) | Klasyfikacja sentymentu, duży wolumen |
| 2D | Ownership | Llama 70B (lokalny) | Ustrukturyzowane dane, powtarzalny format |
| 4A | Bull | Llama 70B (lokalny) | Generowanie argumentów, niskie ryzyko błędu |
| 4B | Bear | Llama 70B (lokalny) | Generowanie argumentów, niskie ryzyko błędu |
| 4C | Pre-Mortem | Llama 70B (lokalny) | Ustrukturyzowane scenariusze |
| 5 | Portfolio Manager | Claude API | Decyzja wysokiego ryzyka, wymaga najlepszego modelu |
| 6 | Feedback Loop | Claude API | Złożona ocena jakościowa, uruchamiany rzadko |

---

## Format danych między warstwami

### Output agentów warstwy 2 (standard dla każdego agenta)

```json
{
  "ticker": "AAPL",
  "agent": "fundamental",
  "timestamp": "2024-01-15T10:30:00Z",
  "score": 7,
  "verdict": "PASS",
  "summary": "Krótkie uzasadnienie (2-3 zdania)",
  "key_risks": ["ryzyko 1", "ryzyko 2"],
  "key_strengths": ["siła 1", "siła 2"],
  "raw_analysis": "Pełna analiza w markdown"
}
```

### Schema decisions_log.json (jeden wpis)

```json
{
  "decision_id": "DEC-042",
  "date": "2024-01-15",
  "ticker": "AAPL",
  "action": "BUY",
  "position_size_pct": 15,
  "entry_price": 185.50,
  "currency": "USD",
  "core_thesis": "Opis tezy w 2-3 zdaniach",
  "key_assumptions": [
    "Założenie 1 — mierzalne, falsifiable",
    "Założenie 2",
    "Założenie 3"
  ],
  "stop_loss_price": 155.00,
  "stop_loss_fundamental": "Opis kiedy teza jest złamana",
  "1yr_checkin_criteria": "Co musi być prawdą po 12 miesiącach",
  "bull_score": 8,
  "bear_score": 4,
  "premortem_top_risk": "Najpoważniejszy scenariusz failure",
  "feedback_6m": null,
  "feedback_12m": null
}
```

---

## Źródła pomysłów na spółki (Warstwa 0)

**Automatyczne screeners:**
- Finviz: market cap $100M–$25B, revenue growth YoY > 15%, insider ownership > 10%
- OpenInsider.com: insider buying (CEO/CFO kupuje za własne pieniądze)
- SEC EDGAR: nowe spin-offy i IPO z ostatnich 18 miesięcy

**Półautomatyczne (wymagają parsowania):**
- 13F filings funduszy $50M–$500M AUM (small, specjalistyczne fundusze)
- Transkrypty konferencji: LD Micro, MicroCap Leadership Summit

**Human input node:**
- Ręczne dodanie do watchlist.json gdy użytkownik odkryje spółkę przez własne doświadczenie
  z produktem (Peter Lynch trigger)

---

## Zasady position sizing

**Twarda zasada:** żadna pojedyncza pozycja nie może przekroczyć 25% portfolio.

---

## Feedback Loop — zasady działania

Uruchamiany automatycznie dla każdej decyzji starszej niż 6 miesięcy gdzie `feedback_6m = null`.

Agent porównuje:
1. Czy `key_assumptions` z dnia decyzji okazały się prawdziwe?
2. Czy cena zmieniła się zgodnie z tezą, czy mimo trafnej tezy, czy mimo błędnej?
3. Które sygnały z warstwy 2 były predyktywne, a które misleading?

Output zapisywany do pól `feedback_6m` i `feedback_12m` w decisions_log.json.

Długoterminowy cel: zidentyfikowanie które agenty i które sygnały mają najwyższą predyktywność
dla danego typu spółek — i odpowiednie dostosowanie wag w warstwie 3.

---

## Decyzje do podjęcia (open questions)

- [ ] Skąd pobierać dane finansowe do agenta fundamental? (Yahoo Finance API, Polygon.io, inne?)
- [ ] Jak często uruchamiać pełny pipeline? (tygodniowo? na żądanie?)
- [ ] Czy system ma obsługiwać spółki polskie (GPW)? Inne źródła danych.
- [ ] Gdzie przechowywać decisions_log.json długoterminowo? (lokalnie, GitHub, baza danych?)
- [ ] Alert system — czy portfolio manager ma wysyłać powiadomienia przy stop-loss?
