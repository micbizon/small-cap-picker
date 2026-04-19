from datetime import date

from .config_loader import load_decisions_log, save_decisions_log


def save_decision(decision: dict) -> None:
    decisions = load_decisions_log()
    decision_id = f"DEC-{len(decisions) + 1:03d}"
    entry = {
        "decision_id": decision_id,
        "date": decision.get("date", str(date.today())),
        **{k: v for k, v in decision.items() if k not in ("decision_id", "date")},
    }
    decisions.append(entry)
    save_decisions_log(decisions)
