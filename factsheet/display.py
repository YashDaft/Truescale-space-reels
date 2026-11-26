"""Turns a fact's value into the text shown on screen, e.g. 1321.33 -> "1,321".

The text is made here by code. Whoever builds a fact sheet (later, an agent)
only chooses how a number is shown, never types the number itself.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from factsheet.schema import Key

SCALES = {"thousand": 1e3, "million": 1e6, "billion": 1e9, "trillion": 1e12}


class DisplayRule(BaseModel):
    """How one fact is shown.

    format:
      number           1321.33 -> "1,321"  (rounded to `decimals`)
      count            4.15 -> "4"         (rounded down: only whole laps, orbits, etc. count)
      percent          0.5316 -> "53%"
      minutes_seconds  499.0 -> "8 minutes 19 seconds"  (the value is in seconds)
    scale: for numbers only, e.g. "million" turns 149598000 into "149.6 million"
    unit:  words after the number, e.g. "km" or "laps". No digits.
    """

    model_config = ConfigDict(extra="forbid")

    fact: Key
    format: Literal["number", "count", "percent", "minutes_seconds"] = "number"
    decimals: int = Field(default=0, ge=0, le=6)
    scale: Literal["thousand", "million", "billion", "trillion"] | None = None
    unit: str = ""

    @model_validator(mode="after")
    def check_options(self):
        if any(character.isdigit() for character in self.unit):
            raise ValueError(f'the unit "{self.unit}" contains a number')
        if self.scale is not None and self.format != "number":
            raise ValueError("a scale can only be used with the number format")
        if self.decimals != 0 and self.format in ("count", "minutes_seconds"):
            raise ValueError(f"the {self.format} format has no decimals")
        return self


def show(rule: DisplayRule, value: float) -> str:
    """The on-screen text for `value`, following `rule`."""
    if rule.format == "minutes_seconds":
        text = _minutes_seconds(value)
    elif rule.format == "percent":
        text = f"{value * 100:,.{rule.decimals}f}%"
    elif rule.format == "count":
        text = f"{int(value):,}"
    else:
        if rule.scale is not None:
            value = value / SCALES[rule.scale]
        text = f"{value:,.{rule.decimals}f}"
        if rule.scale is not None:
            text += f" {rule.scale}"

    if rule.unit:
        text += f" {rule.unit}"
    return text


def _minutes_seconds(seconds: float) -> str:
    if seconds < 0:
        raise ValueError("a duration can't be negative")
    minutes, seconds = divmod(round(seconds), 60)
    seconds_text = f"{seconds} {'second' if seconds == 1 else 'seconds'}"
    if minutes == 0:
        return seconds_text
    return f"{minutes:,} {'minute' if minutes == 1 else 'minutes'} {seconds_text}"
