"""
Per-profile model routing for Agent Zero.

Vanilla Agent Zero gives every agent (superior and every subordinate) the single
model chosen in global settings - `call_subordinate` only swaps the *prompt*
profile, never the model. That makes a heterogeneous "company" of specialists
(each role on a different model) impossible out of the box.

This helper closes that gap. A profile folder may carry an optional
`_config.yaml` describing which model(s) that role should run on:

    # agents/<profile>/_config.yaml
    model:
      chat:                       # the role's main reasoning/acting model
        provider: ollama_cloud
        name: glm-5.2:cloud
        api_base: https://ollama.com
        ctx_length: 200000
        vision: false
        limit_requests: 8         # per-minute cap -> budget / concurrency discipline
        limit_input: 0
        limit_output: 0
        kwargs: {}
      utility:                    # the role's cheap helper model (summaries etc.)
        provider: ollama_cloud
        name: gpt-oss:20b-cloud
        api_base: https://ollama.com

Only keys that are present override the inherited config; anything omitted keeps
the value that came from global settings. A profile with no `_config.yaml` (every
stock profile) behaves exactly as before, so this change is backward compatible.
"""

from __future__ import annotations

import os
from typing import Any, Optional

import yaml

from python.helpers import files


# fields on models.ModelConfig that a profile is allowed to override
_OVERRIDABLE = (
    "provider",
    "name",
    "api_base",
    "ctx_length",
    "limit_requests",
    "limit_input",
    "limit_output",
    "vision",
    "kwargs",
)


def get_profile_config_path(profile: str) -> str:
    return files.get_abs_path("agents", profile, "_config.yaml")


def load_profile_config(profile: str) -> Optional[dict[str, Any]]:
    """Return the parsed `_config.yaml` for a profile, or None if it has none."""
    if not profile:
        return None
    path = get_profile_config_path(profile)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except (OSError, yaml.YAMLError) as e:
        # lazy import so a missing optional print dependency can never break routing
        try:
            from python.helpers.print_style import PrintStyle

            PrintStyle(font_color="red").print(
                f"agent_profile: failed to read {path}: {e}"
            )
        except Exception:
            print(f"agent_profile: failed to read {path}: {e}")
        return None


def _apply_model_overrides(target: "models.ModelConfig", overrides: dict[str, Any]) -> None:
    for key in _OVERRIDABLE:
        if key not in overrides or overrides[key] is None:
            continue
        setattr(target, key, overrides[key])


def apply_profile_model_config(config, profile: str) -> None:
    """
    Mutate an AgentConfig in place, applying the profile's `_config.yaml` model
    overrides to `chat_model` and `utility_model`. No-op when the profile has no
    config or no `model:` section.
    """
    cfg = load_profile_config(profile)
    if not cfg:
        return
    model_cfg = cfg.get("model") or {}
    if not isinstance(model_cfg, dict):
        return

    chat = model_cfg.get("chat")
    if isinstance(chat, dict):
        _apply_model_overrides(config.chat_model, chat)

    util = model_cfg.get("utility")
    if isinstance(util, dict):
        _apply_model_overrides(config.utility_model, util)
