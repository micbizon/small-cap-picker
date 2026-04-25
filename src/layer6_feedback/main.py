import logging
from datetime import date, timedelta

from shared.config_loader import DATA_DIR, load_yaml, save_yaml

from .feedback_agent import run_feedback
from .insights_updater import update_system_insights

logger = logging.getLogger(__name__)

_PROD_LOG = DATA_DIR / "decisions_log.yaml"

_6M = timedelta(days=180)
_12M = timedelta(days=365)


def _parse_date(date_str: str) -> date:
    return date.fromisoformat(str(date_str))


def run_feedback_loop() -> None:
    # Zawsze produkcja — ignoruje RUN_MODE
    decisions = load_yaml(_PROD_LOG).get("decisions", [])
    today = date.today()
    changed = False

    for decision in decisions:
        decision_date = _parse_date(decision["date"])
        age = today - decision_date

        if decision.get("feedback_6m") is None and age > _6M:
            logger.info(f"[feedback] {decision['decision_id']} — ocena 6m")
            result = run_feedback(decision, current_data={}, months=6)
            decision["feedback_6m"] = result
            update_system_insights(result)
            changed = True

        if decision.get("feedback_12m") is None and age > _12M:
            logger.info(f"[feedback] {decision['decision_id']} — ocena 12m")
            result = run_feedback(decision, current_data={}, months=12)
            decision["feedback_12m"] = result
            update_system_insights(result)
            changed = True

    if changed:
        save_yaml(_PROD_LOG, {"decisions": decisions})
        logger.info("[feedback] decisions_log.yaml zaktualizowany")
    else:
        logger.info("[feedback] Brak decyzji wymagających feedbacku")
