"""Works out a fact from a formula such as "earth_sun_km / speed_of_light_km_s".

A formula may only use + - * /, brackets and the names of facts defined
before it. Typed numbers are not allowed, so every number in a worked-out
fact comes from a source fact.
"""

import ast
import operator

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


class FormulaError(ValueError):
    pass


def evaluate(formula: str, values: dict[str, float]) -> float:
    """Calculates `formula` using the fact values in `values`."""
    try:
        tree = ast.parse(formula, mode="eval")
    except SyntaxError:
        raise FormulaError(f'"{formula}" is not a valid formula') from None
    return _calculate(tree.body, values)


def _calculate(node: ast.AST, values: dict[str, float]) -> float:
    if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
        left = _calculate(node.left, values)
        right = _calculate(node.right, values)
        if isinstance(node.op, ast.Div) and right == 0:
            raise FormulaError("the formula divides by zero")
        return OPERATORS[type(node.op)](left, right)

    if isinstance(node, ast.Name):
        if node.id not in values:
            raise FormulaError(f'"{node.id}" is not a fact defined before this one')
        return values[node.id]

    if isinstance(node, ast.Constant):
        raise FormulaError(f"the number {node.value!r} is typed into the formula. Use a fact instead")

    raise FormulaError("a formula may only use + - * /, brackets and fact names")
