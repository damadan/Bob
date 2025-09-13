from json.decoder import JSONDecodeError

import pytest
from jsonschema.exceptions import ValidationError

from core import validate, try_repair_strict_json


VALID_COMPANY = {
    "name": "ACME",
    "site": "https://example.com",
    "registered_at": "2023-01-01",
    "inn": "1234567890",
    "ogrn": "1234567890123",
    "capital": 1000,
    "debt": 0,
    "loss": 0,
    "currency": "RUB",
    "tags": ["a", "b"],
}


# --- tests for validate -----------------------------------------------------


def test_validate_success():
    validate(VALID_COMPANY, "company")


def test_validate_type_error():
    bad = dict(VALID_COMPANY, capital="oops")
    with pytest.raises(ValidationError) as exc:
        validate(bad, "company")
    assert "$.capital" in str(exc.value)


def test_validate_enum_error():
    bad = dict(VALID_COMPANY, currency="EUR")
    with pytest.raises(ValidationError) as exc:
        validate(bad, "company")
    assert "$.currency" in str(exc.value)


def test_validate_required_field():
    bad = dict(VALID_COMPANY)
    del bad["inn"]
    with pytest.raises(ValidationError) as exc:
        validate(bad, "company")
    assert "$.inn" in str(exc.value)


def test_validate_format_errors():
    bad = dict(VALID_COMPANY, registered_at="2023-13-01", site="not-a-uri")
    with pytest.raises(ValidationError) as exc:
        validate(bad, "company")
    # path to the first failing field can be either registered_at or site
    assert any(p in str(exc.value) for p in ("$.registered_at", "$.site"))


def test_validate_pattern_error():
    bad = dict(VALID_COMPANY, inn="123", ogrn="123")
    with pytest.raises(ValidationError) as exc:
        validate(bad, "company")
    assert "$.inn" in str(exc.value)


# --- tests for try_repair_strict_json ---------------------------------------


def base_json_string(extra: str = ""):
    return (
        "{'name': 'ACME', 'site': 'https://example.com',"
        " 'registered_at': '2023-01-01', 'inn': '1234567890',"
        " 'ogrn': '1234567890123', 'currency': 'RUB'" + extra + "}"
    )


def test_repair_handles_bom():
    s = "\ufeff" + base_json_string()
    obj = try_repair_strict_json(s, "company")
    assert obj["name"] == "ACME"


def test_repair_single_quotes():
    s = base_json_string()
    obj = try_repair_strict_json(s, "company")
    assert obj["currency"] == "RUB"


def test_repair_removes_comments():
    s = """
    {
      // comment
      'name': 'ACME', /* block */
      'site': 'https://example.com',
      'registered_at': '2023-01-01', // tail
      'inn': '1234567890',
      'ogrn': '1234567890123',
      'currency': 'RUB'
    }
    """
    obj = try_repair_strict_json(s, "company")
    assert obj["inn"] == "1234567890"


def test_repair_trailing_comma_object():
    s = base_json_string(",")
    obj = try_repair_strict_json(s, "company")
    assert obj["ogrn"] == "1234567890123"


def test_repair_trailing_comma_array():
    s = (
        "{'name': 'ACME', 'site': 'https://example.com',"
        " 'registered_at': '2023-01-01', 'inn': '1234567890',"
        " 'ogrn': '1234567890123', 'currency': 'RUB', 'tags': ['a', 'b',],}"
    )
    obj = try_repair_strict_json(s, "company")
    assert obj["tags"] == ["a", "b"]


def test_repair_nan_and_infinity():
    s = (
        "{'name': 'ACME', 'site': 'https://example.com',"
        " 'registered_at': '2023-01-01', 'inn': '1234567890',"
        " 'ogrn': '1234567890123', 'currency': 'RUB',"
        " 'capital': NaN, 'debt': Infinity, 'loss': -Infinity}"
    )
    obj = try_repair_strict_json(s, "company")
    assert obj["capital"] is None
    assert obj["debt"] is None and obj["loss"] is None


def test_repair_invalid_date():
    s = base_json_string().replace("2023-01-01", "2023-13-01")
    with pytest.raises(ValidationError):
        try_repair_strict_json(s, "company")


def test_repair_invalid_inn():
    s = base_json_string().replace("1234567890", "12")
    with pytest.raises(ValidationError):
        try_repair_strict_json(s, "company")


def test_repair_parse_error():
    s = "{'name': 'ACME'"  # missing closing brace
    with pytest.raises(JSONDecodeError):
        try_repair_strict_json(s, "company")


def test_repair_handles_escape_sequences():
    s = (
        "{'name': 'ACME', 'site': 'https://example.com',"
        " 'registered_at': '2023-01-01', 'inn': '1234567890',"
        " 'ogrn': '1234567890123', 'currency': 'RUB',"
        " 'tags': ['a\\\\b']}"
    )
    obj = try_repair_strict_json(s, "company")
    assert obj["tags"][0] == "a\\b"
