{{ CORE_RULES }}

Rok [FUTURE_YEAR]. [TICKER] straciło 65%. Odtwórz co poszło nie tak.
Pracuj wstecz od porażki. Szukaj blind spotów których bull/bear nie złapały.

Kontekst: [LAYER2_CONTEXT]

Zwróć wyłącznie JSON:
{
  "ticker": "",
  "agent": "premortem",
  "failure_scenarios": [
    {
      "rank": 1,
      "description": "MAX 8 słów — nazwa scenariusza.",
      "mechanism": "MAX 2 zdania — krok po kroku.",
      "type": "company-specific|sector-wide|macro",
      "probability": "LOW|MEDIUM|HIGH",
      "earliest_warning_signal": "MAX 1 zdanie. Mierzalny sygnał z progiem."
    }
  ],
  "top_blind_spot": "MAX 1 zdanie.",
  "raw_analysis": "MAX 75 słów."
}
