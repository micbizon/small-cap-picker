{{ CORE_RULES }}

Otrzymujesz [N] niezależnych analiz bear case dla [TICKER].
Twoim zadaniem jest synteza — nie uśrednianie, lecz wyciąganie sygnału z szumu.

ANALIZY DO SYNTEZY:
[BEAR_ANALYSES]

Wykonaj w tej kolejności:

1. KONSENSUS: Ryzyka obecne w minimum 2 z [N] analiz.
   To są twarde zagrożenia dla tezy — wysoka pewność.

2. UNIKALNE SYGNAŁY: Ryzyka obecne tylko w jednej analizie.
   Oceń każdy: czy to przeoczony czynnik czy halucynacja?
   Oznacz jako WARTO_ZBADAĆ lub ODRZUCAM z jednozdaniowym powodem.

3. SPRZECZNOŚCI: Miejsca gdzie analizy się kłócą.
   Wskaż co jest sprzeczne i która wersja wydaje się bardziej ugruntowana w faktach.

4. SYNTETYCZNY BEAR CASE: Jeden spójny raport bazujący na powyższym.
   Nie powtarzaj treści z kroków 1-3 — napisz narrację która z nich wynika.

Zwróć wyłącznie JSON:
{
  "ticker": "",
  "agent": "bear",
  "score": 0,
  "central_bear_thesis": "",
  "top_competitive_threat": "",
  "financial_stress_result": "",
  "macro_sensitivity": "",
  "exit_liquidity_risk": "LOW|MEDIUM|HIGH",
  "what_would_change_mind": "",
  "key_risks": [],
  "consensus_strength": "HIGH|MEDIUM|LOW",
  "raw_analysis": ""
}

Zasady wypełnienia:
- score: średnia ważona (konsensus liczy 2x, unikalne 0.5x)
- key_risks: tylko te z sekcji KONSENSUS
- consensus_strength: "HIGH" jeśli spread score'ów <=2, "MEDIUM" jeśli <=4, "LOW" jeśli >4
- raw_analysis: narracja z kroku 4 (SYNTETYCZNY BEAR CASE)
