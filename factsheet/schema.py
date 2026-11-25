"""The shape of a fact sheet and the rules every fact sheet must follow.

The renderer reads the same JSON (see renderer/src/types.ts), so the field
names here must stay the same as there.
"""

import json
import math
from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, FiniteFloat, StringConstraints, model_validator

from factsheet.formula import FormulaError, evaluate

# How a fact was established. The reel shows this next to the fact.
Level = Literal["measured data", "official release", "peer-reviewed paper", "preprint"]

# The same pattern the renderer uses for {placeholders}
KEY_PATTERN = "[a-z0-9_]+"
Key = Annotated[str, StringConstraints(pattern=f"^{KEY_PATTERN}$")]

Url = Annotated[str, StringConstraints(pattern=r"^https?://\S+$")]


class Fact(BaseModel):
    """One number. Either copied from a source, or worked out from other facts."""

    model_config = ConfigDict(extra="forbid")

    value: FiniteFloat
    source: Url | None = None  # link to the official source
    level: Level | None = None
    formula: str | None = None  # for facts worked out from other facts

    @model_validator(mode="after")
    def source_or_formula(self):
        if self.formula is None:
            if self.source is None or self.level is None:
                raise ValueError("a fact needs a source link and a level, or a formula")
        elif self.source is not None or self.level is not None:
            raise ValueError("a worked-out fact has a formula only, no source or level")
        return self


class FactSheet(BaseModel):
    """Every number a reel may use, plus the text that shows them on screen."""

    model_config = ConfigDict(extra="forbid")

    facts: dict[Key, Fact]
    display: dict[Key, Annotated[str, StringConstraints(min_length=1)]]

    @model_validator(mode="after")
    def formulas_match_values(self):
        # Each formula is worked out again from the facts listed before it.
        # This catches a value that was changed by hand after it was calculated.
        problems = []
        earlier = {}
        for key, fact in self.facts.items():
            if fact.formula is not None:
                try:
                    expected = evaluate(fact.formula, earlier)
                except FormulaError as error:
                    problems.append(f"{key}: {error}")
                else:
                    if not math.isclose(fact.value, expected, rel_tol=1e-9):
                        problems.append(f"{key}: the value {fact.value} doesn't match its formula, which gives {expected}")
            earlier[key] = fact.value
        if problems:
            raise ValueError("; ".join(problems))
        return self

    def to_json(self) -> str:
        """The JSON the renderer reads."""
        return json.dumps(self.model_dump(exclude_none=True), indent=2) + "\n"


def load(path: str | Path) -> FactSheet:
    """Reads a fact sheet file and checks every rule above."""
    return FactSheet.model_validate_json(Path(path).read_text())
