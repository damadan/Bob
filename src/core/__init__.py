"""Core utilities for JSON validation used in tests."""

from .validator import validate, try_repair_strict_json

__all__ = ["validate", "try_repair_strict_json"]
