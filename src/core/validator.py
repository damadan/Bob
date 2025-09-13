"""Validation helpers for project schemas.

This module provides two public functions:

``validate(obj, schema_name)``
    Validate a Python ``dict`` against the named JSON schema.  Raises
    :class:`jsonschema.exceptions.ValidationError` with a message containing
    the failing JSON path when validation does not succeed.

``try_repair_strict_json(s, schema_name)``
    Attempt to repair a slightly malformed JSON string, parse it and then
    validate it against the schema.  Only the following defects are corrected:

    * UTF-8 BOM at the beginning of the string.
    * Surrounding whitespace.
    * Single quotes used for keys or string values.
    * JavaScript style comments (``//`` and ``/* ... */``).
    * Trailing commas in objects and arrays.
    * ``NaN``, ``Infinity`` and ``-Infinity`` literals (replaced with ``null``).

Any other structural issues result in an immediate parsing error.  After repair
and parsing the resulting object is validated using :func:`validate`.
"""

from __future__ import annotations

from dataclasses import dataclass
import copy
import json
import re
from typing import Any, Dict

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import ValidationError

from .schemas import load_schema

try:  # optional, for faster parsing if available
    import orjson  # type: ignore
except Exception:  # pragma: no cover - fallback branch
    orjson = None  # type: ignore


@dataclass
class _ParserState:
    """Simple state machine for stripping comments and literals."""

    in_string: bool = False
    escape: bool = False
    string_char: str = ""
    in_line_comment: bool = False
    in_block_comment: bool = False


def validate(obj: Dict[str, Any], schema_name: str) -> None:
    """Validate ``obj`` against schema ``schema_name``.

    Parameters
    ----------
    obj:
        Python dictionary representing JSON data.  The object is not modified.
    schema_name:
        Name of the schema file without ``.schema.json`` extension.

    Raises
    ------
    jsonschema.exceptions.ValidationError
        If the object does not conform to the schema.  The error message
        contains the failing JSON path and a readable description.
    """

    schema = load_schema(schema_name)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    try:
        validator.validate(copy.deepcopy(obj))
    except ValidationError as exc:  # pragma: no cover - exercised in tests
        path = exc.json_path
        if exc.validator == "required" and "required property" in exc.message:
            missing = exc.message.split("'", 2)[1]
            path = f"{path}.{missing}" if path != "$" else f"$.{missing}"
        exc.message = f"{path}: {exc.message}"
        raise


def _replace_single_quotes(text: str) -> str:
    """Replace single-quoted strings with double quotes."""

    def repl(match: re.Match[str]) -> str:
        inner = match.group(1).replace("\\'", "'")
        return f'"{inner}"'

    return re.sub(r"(?<!\\)'([^'\\]*(?:\\.[^'\\]*)*)'", repl, text)


def _strip_comments_and_commas(text: str) -> str:
    state = _ParserState()
    result: list[str] = []
    i = 0
    length = len(text)
    while i < length:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < length else ""
        if state.in_string:
            result.append(ch)
            if state.escape:
                state.escape = False
            elif ch == "\\":
                state.escape = True
            elif ch == state.string_char:
                state.in_string = False
            i += 1
            continue
        if state.in_line_comment:
            if ch in "\n\r":
                state.in_line_comment = False
            i += 1
            continue
        if state.in_block_comment:
            if ch == "*" and nxt == "/":
                state.in_block_comment = False
                i += 2
            else:
                i += 1
            continue
        if ch == "/" and nxt == "/":
            state.in_line_comment = True
            i += 2
            continue
        if ch == "/" and nxt == "*":
            state.in_block_comment = True
            i += 2
            continue
        if ch in {'"', "'"}:
            state.in_string = True
            state.string_char = ch
            result.append(ch)
            i += 1
            continue
        result.append(ch)
        i += 1
    cleaned = "".join(result)
    # Remove trailing commas in objects and arrays
    cleaned = re.sub(r",(\s*[}\]])", r"\1", cleaned)
    return cleaned


def _replace_invalid_literals(text: str) -> str:
    state = _ParserState()
    result: list[str] = []
    i = 0
    length = len(text)
    while i < length:
        ch = text[i]
        if state.in_string:
            result.append(ch)
            if state.escape:
                state.escape = False
            elif ch == "\\":
                state.escape = True
            elif ch == state.string_char:
                state.in_string = False
            i += 1
            continue
        if ch in {'"', "'"}:
            state.in_string = True
            state.string_char = ch
            result.append(ch)
            i += 1
            continue
        if text.startswith("-Infinity", i):
            result.append("null")
            i += 9
            continue
        if text.startswith("Infinity", i):
            result.append("null")
            i += 8
            continue
        if text.startswith("NaN", i):
            result.append("null")
            i += 3
            continue
        result.append(ch)
        i += 1
    return "".join(result)


def try_repair_strict_json(s: str, schema_name: str) -> Dict[str, Any]:
    """Repair a slightly malformed JSON string and validate it.

    Parameters
    ----------
    s:
        String containing JSON data with possible minor defects listed in the
        module documentation.
    schema_name:
        Name of the JSON schema used for validation.

    Returns
    -------
    dict
        Parsed JSON object.

    Raises
    ------
    json.decoder.JSONDecodeError
        If the string cannot be parsed into JSON after repair.
    jsonschema.exceptions.ValidationError
        If the parsed object does not conform to the schema.
    """

    s = s.lstrip("\ufeff").strip()
    s = _replace_single_quotes(s)
    s = _strip_comments_and_commas(s)
    s = _replace_invalid_literals(s)

    try:
        if orjson is not None:  # pragma: no cover - optional branch
            obj = orjson.loads(s)
        else:  # pragma: no cover - optional branch
            obj = json.loads(s)
    except json.JSONDecodeError as exc:  # pragma: no cover - tested via raise
        raise exc

    validate(obj, schema_name)
    return obj
