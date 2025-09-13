"""Utilities for loading JSON schemas used in tests."""

from __future__ import annotations

import json
from importlib import resources
from typing import Any, Dict


def load_schema(name: str) -> Dict[str, Any]:
    """Load a JSON schema by ``name``.

    The function looks for ``"{name}.schema.json"`` inside this package and
    returns the parsed dictionary.
    """
    with (
        resources.files(__package__)
        .joinpath(f"{name}.schema.json")
        .open("r", encoding="utf-8") as f
    ):
        return json.load(f)
