#!/usr/bin/env python3
"""Day 45: Simple Calculator.

Evaluates arithmetic expressions safely (no eval) using Python's ast module.
Supports + - * / // % ** and parentheses.
"""

from __future__ import annotations

import ast
import operator
import sys

OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}
UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 1000:
            raise ValueError("exponent too large")
        return OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY:
        return UNARY[type(node.op)](_eval(node.operand))
    raise ValueError("unsupported expression")


def calculate(expr: str) -> float:
    """Return the value of an arithmetic expression string."""
    tree = ast.parse(expr.strip(), mode="eval")
    return _eval(tree)


def fmt(value: float) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(round(value, 10)) if isinstance(value, float) else str(value)


def run(expr: str) -> int:
    try:
        print(f"{expr} = {fmt(calculate(expr))}")
        return 0
    except ZeroDivisionError:
        print("Error: division by zero", file=sys.stderr)
    except (SyntaxError, ValueError) as exc:
        print(f"Error: {exc if isinstance(exc, ValueError) else 'invalid syntax'}", file=sys.stderr)
    return 1


def main() -> int:
    if len(sys.argv) > 1:
        return run(" ".join(sys.argv[1:]))
    print("Simple Calculator (type 'q' to quit)")
    while True:
        try:
            expr = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if expr.lower() in {"q", "quit", "exit"}:
            return 0
        if expr:
            run(expr)


if __name__ == "__main__":
    sys.exit(main())
