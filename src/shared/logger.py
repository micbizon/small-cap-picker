from datetime import date

from .config_loader import load_decisions_log, save_decisions_log

_DECISION_FIELDS = (
    "ticker",
    "action",
    "current_position_size_pct",
    "target_position_size_pct",
    "entry_price",
    "entry_price_currency",
    "rationale",
    "stop_loss_price",
    "stop_loss_fundamental",
    "checkin_1yr_criteria",
    "feedback_6m",
    "feedback_12m",
)


def save_decision(decision: dict) -> None:
    if decision.get("action") == "PASS":
        return
    decisions = load_decisions_log()
    decision_id = f"DEC-{len(decisions) + 1:03d}"
    entry = {
        "decision_id": decision_id,
        "date": decision.get("date", str(date.today())),
        **{k: decision[k] for k in _DECISION_FIELDS if k in decision},
    }
    decisions.append(entry)
    save_decisions_log(decisions)
