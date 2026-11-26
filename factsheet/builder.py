"""Builds a fact sheet one fact at a time.

Every problem is collected instead of stopping at the first one, so whoever
is building the sheet (later, an agent) can fix all of them in one go.
"""

import re
from pathlib import Path

from pydantic import ValidationError

from factsheet.display import DisplayRule, show
from factsheet.formula import FormulaError, evaluate
from factsheet.schema import KEY_PATTERN, Fact, FactSheet, Level


class FactSheetError(ValueError):
    def __init__(self, problems: list[str]):
        self.problems = problems
        super().__init__(f"The fact sheet has {len(problems)} problem(s):\n- " + "\n- ".join(problems))


class FactSheetBuilder:
    def __init__(self):
        self._facts: dict[str, Fact] = {}
        self._display: dict[str, str] = {}
        self._problems: list[str] = []

    def add_source_fact(self, key: str, value: float, source: str, level: Level) -> None:
        """A number copied from an official source."""
        if self._is_new(key, self._facts):
            self._add_fact(key, value=value, source=source, level=level)

    def add_worked_out(self, key: str, formula: str) -> None:
        """A number calculated from facts added before it, e.g. "earth_sun_km / speed_of_light_km_s"."""
        if not self._is_new(key, self._facts):
            return
        values = {name: fact.value for name, fact in self._facts.items()}
        try:
            value = evaluate(formula, values)
        except FormulaError as error:
            self._problems.append(f"{key}: {error}")
            return
        self._add_fact(key, value=value, formula=formula)

    def add_display(
        self,
        key: str,
        fact: str,
        format: str = "number",
        decimals: int = 0,
        scale: str | None = None,
        unit: str = "",
    ) -> None:
        """On-screen text for a fact, made by code. See DisplayRule for the options."""
        if not self._is_new(key, self._display):
            return
        try:
            rule = DisplayRule(fact=fact, format=format, decimals=decimals, scale=scale, unit=unit)
        except ValidationError as error:
            self._add_errors(key, error)
            return
        if rule.fact not in self._facts:
            self._problems.append(f'{key}: "{rule.fact}" is not in the fact sheet')
            return
        try:
            self._display[key] = show(rule, self._facts[rule.fact].value)
        except ValueError as error:
            self._problems.append(f"{key}: {error}")

    def build(self) -> FactSheet:
        """The finished fact sheet. Raises FactSheetError listing every problem."""
        if self._problems:
            raise FactSheetError(self._problems)
        return FactSheet(facts=self._facts, display=self._display)

    def save(self, path: str | Path) -> FactSheet:
        """Builds the fact sheet and writes it as JSON for the renderer."""
        sheet = self.build()
        Path(path).write_text(sheet.to_json())
        return sheet

    def _is_new(self, key: str, existing: dict) -> bool:
        if not re.fullmatch(KEY_PATTERN, key):
            self._problems.append(f'"{key}": a key may only use a-z, 0-9 and _')
            return False
        if key in existing:
            self._problems.append(f'"{key}" was added twice')
            return False
        return True

    def _add_fact(self, key: str, **fields) -> None:
        try:
            self._facts[key] = Fact(**fields)
        except ValidationError as error:
            self._add_errors(key, error)

    def _add_errors(self, key: str, error: ValidationError) -> None:
        for problem in error.errors():
            where = ".".join(str(part) for part in problem["loc"])
            self._problems.append(f"{key}, {where}: {problem['msg']}" if where else f"{key}: {problem['msg']}")
