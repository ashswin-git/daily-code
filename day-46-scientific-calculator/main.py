#!/usr/bin/env python3
"""Scientific Calculator: safe expression evaluator with math functions."""
import ast
import math
import operator
import sys

BIN = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
       ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
       ast.Mod: operator.mod, ast.Pow: operator.pow}
UN = {ast.UAdd: operator.pos, ast.USub: operator.neg}
CONST = {"pi": math.pi, "e": math.e, "tau": math.tau}
FUNCS = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
    "sqrt": math.sqrt, "log": math.log10, "ln": math.log, "exp": math.exp,
    "abs": abs, "fact": math.factorial, "floor": math.floor, "ceil": math.ceil,
    "round": round, "deg": math.degrees, "rad": math.radians,
}


def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in BIN:
        return BIN[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in UN:
        return UN[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.Name) and node.id in CONST:
        return CONST[node.id]
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id in FUNCS and not node.keywords):
        return FUNCS[node.func.id](*[_eval(a) for a in node.args])
    raise ValueError("unsupported expression")


def calculate(expr):
    return _eval(ast.parse(expr.strip().replace("^", "**"), mode="eval"))


def show(expr):
    try:
        res = calculate(expr)
        if isinstance(res, float):
            res = round(res, 10)
        print(f"{expr} = {res}")
    except ZeroDivisionError:
        print("Error: division by zero")
    except (ValueError, SyntaxError, TypeError, OverflowError) as exc:
        print(f"Error: {exc}")


def main():
    if len(sys.argv) > 1:
        show(" ".join(sys.argv[1:]))
        return
    print("Scientific Calculator. Functions: " + ", ".join(FUNCS))
    print("Constants: pi, e, tau. Type 'quit' to exit.")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if line.lower() in ("quit", "exit", "q"):
            break
        if line:
            show(line)


if __name__ == "__main__":
    main()
