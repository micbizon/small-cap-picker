{{ CORE_RULES }}

Otrzymujesz [N] niezależnych analiz bull case dla [TICKER].
Twoim zadaniem jest synteza — nie uśrednianie, lecz wyciąganie sygnału z szumu.

ANALIZY DO SYNTEZY:
[BULL_ANALYSES]

Wykonaj w tej kolejności:

1. KONSENSUS: Argumenty obecne w minimum 2 z [N] analiz.
   To są twarde punkty tezy — wysoka pewność.

2. UNIKALNE SYGNAŁY: Argumenty obecne tylko w jednej analizie.
   Oceń każdy: czy to przeoczony czynnik czy halucynacja?
   Oznacz jako WARTO_ZBADAĆ lub ODRZUCAM z jednozdaniowym powodem.

3. SPRZECZNOŚCI: Miejsca gdzie analizy się kłócą.
   Wskaż co jest sprzeczne i która wersja wydaje się bardziej ugruntowana w faktach.

4. SYNTETYCZNY BULL CASE: Jeden spójny raport bazujący na powyższym.
   Nie powtarzaj treści z kroków 1-3 — napisz narrację która z nich wynika.

Zwróć wyłącznie JSON:
{
  "ticker": "",
  "agent": "bull",
  "score": 0,
  "core_thesis": "",
  "flywheel_mechanism": "",
  "underappreciated_factor": "",
  "historical_analogs": [],
  "price_target_3yr": 0,
  "key_assumptions": [],
  "consensus_strength": "HIGH|MEDIUM|LOW",
  "raw_analysis": ""
}

Zasady wypełnienia:
- score: średnia ważona (konsensus liczy 2x, unikalne 0.5x)
- key_assumptions: tylko te z sekcji KONSENSUS
- underappreciated_factor: najlepszy sygnał z UNIKALNE SYGNAŁY oznaczony WARTO_ZBADAĆ (lub null jeśli brak)
- consensus_strength: "HIGH" jeśli spread score'ów <=2, "MEDIUM" jeśli <=4, "LOW" jeśli >4
- raw_analysis: narracja z kroku 4 (SYNTETYCZNY BULL CASE)
