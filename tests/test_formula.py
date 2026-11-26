import pytest

from factsheet import FormulaError, evaluate

VALUES = {"a": 6.0, "b": 2.0, "c": 0.0}


def test_works_out_arithmetic_with_fact_names():
    assert evaluate("a / b", VALUES) == 3.0
    assert evaluate("(a + b) * b - a", VALUES) == 10.0


def test_same_result_as_python():
    # The renderer's example fact sheet depends on this exact float
    assert evaluate("a / b", {"a": 149598000.0, "b": 299792.458}) == 149598000.0 / 299792.458


@pytest.mark.parametrize(
    ("formula", "message"),
    [
        ("a * 100", "typed into the formula"),
        ("a ** b", "may only use"),
        ("abs(a)", "may only use"),
        ("-a", "may only use"),
        ("a.real", "may only use"),
        ("d / a", '"d" is not a fact'),
        ("a / c", "divides by zero"),
        ("a /", "not a valid formula"),
    ],
)
def test_refuses_anything_else(formula, message):
    with pytest.raises(FormulaError, match=message):
        evaluate(formula, VALUES)
