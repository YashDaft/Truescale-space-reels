import pytest
from pydantic import ValidationError

from factsheet import DisplayRule, show


def text(value, **options):
    return show(DisplayRule(fact="x", **options), value)


def test_number():
    assert text(1321.33) == "1,321"
    assert text(10.973, decimals=2) == "10.97"
    assert text(149598000.0, decimals=1, scale="million", unit="km") == "149.6 million km"


def test_count_rounds_down():
    # Mercury finishes 4 laps in an Earth year, not 5
    assert text(4.85, format="count", unit="laps") == "4 laps"
    assert text(12345.9, format="count") == "12,345"


def test_percent():
    assert text(0.5316, format="percent") == "53%"
    assert text(0.5316, format="percent", decimals=1) == "53.2%"


def test_minutes_seconds():
    assert text(499.005, format="minutes_seconds") == "8 minutes 19 seconds"
    assert text(61.0, format="minutes_seconds") == "1 minute 1 second"
    assert text(42.0, format="minutes_seconds") == "42 seconds"


def test_negative_duration_is_refused():
    with pytest.raises(ValueError, match="negative"):
        text(-5.0, format="minutes_seconds")


@pytest.mark.parametrize(
    ("options", "message"),
    [
        ({"unit": "km in 2024"}, "contains a number"),
        ({"format": "percent", "scale": "million"}, "only be used with the number format"),
        ({"format": "count", "decimals": 2}, "has no decimals"),
        ({"format": "fraction"}, "format"),
        ({"decimals": 9}, "decimals"),
    ],
)
def test_bad_rules_are_refused(options, message):
    with pytest.raises(ValidationError, match=message):
        DisplayRule(fact="x", **options)
