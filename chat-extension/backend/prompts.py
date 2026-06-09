from pathlib import Path

_BASE = Path(__file__).parent.parent.parent  # repo root: athena/
HUMANIZE = (_BASE / "skills/guardrails/HUMANIZE.md").read_text()
DEVELOPER = (_BASE / "skills/persona-rewrite/DEVELOPER.md").read_text()


def build_messages(messages: list[dict], config) -> list[dict]:
    system = []
    if config.humanize:
        system.append({"role": "system", "content": HUMANIZE})
    if config.developer:
        system.append({"role": "system", "content": DEVELOPER})
    return system + messages
