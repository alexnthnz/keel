#!/usr/bin/env python3
"""Check that the Codex package still points at the intended Keel files."""

import json
import re
import sys
from pathlib import Path


ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) == 2 else Path(__file__).resolve().parents[2]
CODEX_SKILLS = "./codex/skills/"
ADAPTER = "codex/skills/lead/SKILL.md"
MARKDOWN_LINK = re.compile(r"\]\(([^)\s]+)")
URL_SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")
CODEX_HOOKS = "./codex/hooks/hooks.json"
REMINDER_HOOKS = {
    "UserPromptSubmit": [{"hooks": [{"type": "command", "command": 'sh "${PLUGIN_ROOT}/codex/hooks/lead-reminder.sh"'}]}],
}


def read_json(path: str, errors: list[str]) -> dict:
    try:
        value = json.loads((ROOT / path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"{path}: {exc}")
        return {}
    if not isinstance(value, dict):
        errors.append(f"{path}: expected a JSON object")
        return {}
    return value


def adapter_link_errors() -> list[str]:
    adapter = ROOT / ADAPTER
    errors = []
    for target in MARKDOWN_LINK.findall(adapter.read_text(encoding="utf-8")):
        if URL_SCHEME.match(target):
            continue
        resolved = (adapter.parent / target.partition("#")[0]).resolve()
        if not resolved.is_relative_to(ROOT) or not resolved.exists():
            errors.append(f"{ADAPTER}: link {target} does not resolve to a file or directory in the package")
    return errors


def main() -> int:
    errors: list[str] = []

    for path in ("plugin.json", ".agents/plugins/marketplace.json"):
        if (ROOT / path).exists():
            errors.append(f"{path}: unexpected; keep the Codex overlay separate from Claude skills and marketplace")

    codex = read_json(".codex-plugin/plugin.json", errors)
    claude = read_json(".claude-plugin/plugin.json", errors)
    marketplace = read_json(".claude-plugin/marketplace.json", errors)

    for path, manifest in ((".codex-plugin/plugin.json", codex), (".claude-plugin/plugin.json", claude)):
        if manifest and manifest.get("name") != "keel":
            errors.append(f"{path}: name must be keel")

    entries = marketplace.get("plugins")
    keel_entries = [entry for entry in entries if isinstance(entry, dict) and entry.get("name") == "keel"] if isinstance(entries, list) else []
    if len(keel_entries) != 1:
        errors.append(".claude-plugin/marketplace.json: expected exactly one keel plugin entry")

    versions = {
        ".codex-plugin/plugin.json": codex.get("version"),
        ".claude-plugin/plugin.json": claude.get("version"),
        ".claude-plugin/marketplace.json": keel_entries[0].get("version") if len(keel_entries) == 1 else None,
    }
    if any(not isinstance(version, str) or not version for version in versions.values()) or len(set(versions.values())) != 1:
        errors.append("Keel versions differ or are missing: " + ", ".join(f"{path}={version!r}" for path, version in versions.items()))

    if codex.get("skills") != CODEX_SKILLS:
        errors.append(f".codex-plugin/plugin.json: skills must be {CODEX_SKILLS}")
    elif not (ROOT / ADAPTER).is_file():
        errors.append(f"{ADAPTER}: missing")
    else:
        errors += adapter_link_errors()

    if codex.get("hooks") != CODEX_HOOKS:
        errors.append(f".codex-plugin/plugin.json: hooks must be {CODEX_HOOKS}")
    if read_json("codex/hooks/hooks.json", errors).get("hooks") != REMINDER_HOOKS:
        errors.append(f"codex/hooks/hooks.json: \"hooks\" must be exactly {json.dumps(REMINDER_HOOKS)}")
    if not (ROOT / "codex/hooks/lead-reminder.sh").is_file():
        errors.append("codex/hooks/lead-reminder.sh: missing")

    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    print("Codex package paths and versions match Keel's Claude package.")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 2:
        raise SystemExit("usage: validate-package.py [repo-root]")
    raise SystemExit(main())
