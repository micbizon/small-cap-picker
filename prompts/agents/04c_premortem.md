{{ CORE_RULES }}

Mamy rok [FUTURE_YEAR]. Zainwestowaliśmy w [TICKER] i akcja straciła 65%.
Inwestycja zakończyła się porażką.

Kontekst z analizy: [LAYER2_CONTEXT]

Twoim zadaniem jest odtworzenie CO POSZŁO NIE TAK — pracując wstecz od porażki.
To nie jest przewidywanie że spółka straci. To ćwiczenie identyfikacji
blind spotów których bull i bear case mogły nie złapać.

Zidentyfikuj 3 scenariusze porażki. Każdy musi zawierać:
- Mechanikę: co dokładnie się stało krok po kroku
- Typ: "company-specific" / "sector-wide" / "macro"
- Prawdopodobieństwo: LOW / MEDIUM / HIGH
- Najwcześniejszy sygnał ostrzegawczy: co wykryć zanim będzie za późno

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
