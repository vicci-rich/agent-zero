"""
Custom behaviour ruleset - single source of truth.

Agent Zero persists a per-memory-subdir "behaviour" ruleset at
`memory/<subdir>/behaviour.md` and injects it at the TOP of the system prompt on
every message loop (see extensions/system_prompt/_20_behaviour_prompt.py). Because
it lives in the memory dir - not the chat - it survives chat deletion, project
removal and restarts. That makes it powerful but also a silent failure mode: one
bad rule written by `behaviour_adjustment` keeps steering every future session
until the file itself is cleared.

This module centralises reading/writing/resetting that file so both the injection
extension and the adjustment tool behave identically, and hardens it:
  - RAW read (no templating): a poisoned `{{ ... }}` / `!include` in the ruleset
    can neither expand nor crash the prompt build.
  - fail-safe: any read error falls back to the built-in default instead of
    breaking the loop.
  - size-capped: a runaway ruleset cannot dominate / blow up the context window.
  - resettable: `reset_rules()` reverts to the default, so a poisoned ruleset can
    be cleared from within a chat (behaviour_adjustment reset) with no shell access.
"""

import os

from python.helpers import files, memory
from python.helpers.print_style import PrintStyle

# a legitimate ruleset is a short bullet list; cap well above that so a corrupt or
# runaway merge can't silently take over the system prompt
MAX_RULES_CHARS = 10000


def get_custom_rules_file(agent) -> str:
    return memory.get_memory_subdir_abs(agent) + "/behaviour.md"


def has_custom_rules(agent) -> bool:
    return files.exists(get_custom_rules_file(agent))


def read_custom_rules(agent):
    """Return the raw custom ruleset, or None if there is no usable one."""
    path = get_custom_rules_file(agent)
    if not files.exists(path):
        return None
    try:
        rules = files.read_file(path)  # raw: never template a persisted, mutable file
    except Exception as e:
        PrintStyle(font_color="red").print(
            f"behaviour: could not read {path}, falling back to default rules: {e}"
        )
        return None
    if not rules or not rules.strip():
        return None
    if len(rules) > MAX_RULES_CHARS:
        PrintStyle(font_color="red").print(
            f"behaviour: ruleset at {path} is {len(rules)} chars (> {MAX_RULES_CHARS}); truncating"
        )
        rules = rules[:MAX_RULES_CHARS]
    return rules


def read_rules(agent) -> str:
    """Ruleset wrapped for the system prompt; the built-in default when none is set."""
    rules = read_custom_rules(agent)
    if rules is None:
        rules = agent.read_prompt("agent.system.behaviour_default.md")
    return agent.read_prompt("agent.system.behaviour.md", rules=rules)


def write_rules(agent, rules: str) -> None:
    files.write_file(get_custom_rules_file(agent), rules or "")


def reset_rules(agent) -> bool:
    """Delete the custom ruleset so behaviour reverts to default. True if one existed."""
    path = get_custom_rules_file(agent)
    if not files.exists(path):
        return False
    try:
        os.remove(path)
    except OSError:
        files.write_file(path, "")  # best-effort: blank it so read falls back to default
    return True
