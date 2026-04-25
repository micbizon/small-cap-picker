from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"


def _load_response_rules() -> str:
    return (PROMPTS_DIR / "RESPONSE_RULES.md").read_text(encoding="utf-8")


def load_core_rules() -> str:
    return (
        (PROMPTS_DIR / "CORE_RULES.md").read_text(encoding="utf-8")
        + "\n"
        + _load_response_rules()
    )
