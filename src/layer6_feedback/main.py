from datetime import date, timedelta

from shared.config_loader import load_decisions_log, save_decisions_log

from .feedback_agent import run_feedback
from .insights_updater import update_system_insights

_6M = timedelta(days=180)
_12M = timedelta(days=365)


def _parse_date(date_str: str) -> date:
    return date.fromisoformat(str(date_str))


def run_feedback_loop() -> None:
    decisions = load_decisions_log()
    today = date.today()
    changed = False

    for decision in decisions:
        decision_date = _parse_date(decision["date"])
        age = today - decision_date

        if decision.get("feedback_6m") is None and age > _6M:
            print(f"[feedback] {decision['decision_id']} — ocena 6m")
            result = run_feedback(decision, current_data={}, months=6)
            decision["feedback_6m"] = result
            update_system_insights(result)
            changed = True

        if decision.get("feedback_12m") is None and age > _12M:
            print(f"[feedback] {decision['decision_id']} — ocena 12m")
            result = run_feedback(decision, current_data={}, months=12)
            decision["feedback_12m"] = result
            update_system_insights(result)
            changed = True

    if changed:
        save_decisions_log(decisions)
        print("[feedback] decisions_log.yaml zaktualizowany")
    else:
        print("[feedback] Brak decyzji wymagających feedbacku")
