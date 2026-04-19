from pathlib import Path

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"


def load_core_rules() -> str:
    with open(PROMPTS_DIR / "CORE_RULES.md", "r", encoding="utf-8") as f:
        return f.read()
