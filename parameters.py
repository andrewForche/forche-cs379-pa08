"""
PA 7: The Parameter Simulator -- starter.

Complete bind_parameters, commit_value_result, and Closure below.
Cell, evaluate(), and FunctionDecl are already provided -- do not
modify them. See the assignment, Part B, for the
full requirements.

Value-result binding has two steps: bind_parameters runs at call time
and records each caller destination; commit_value_result runs after
the simulated body and copies the final local values back in parameter
order. The handout specifies both steps.

Design note 2: variables are stored as Cell objects (a mutable box),
not raw values, specifically so reference-mode parameters can share
the exact same storage as the caller's variable -- see Part A,
Questions 1-2, for why "bind directly to the caller's slot" requires
this instead of just copying a plain value.
"""

from typing import Any, List, Tuple

from parser import BinOp, Number, Variable
from symtable import Environment


class Cell:
    """Given: a mutable box. Two names that share the SAME Cell are aliased."""

    __slots__ = ("value",)

    def __init__(self, value: Any) -> None:
        self.value = value


class FunctionDecl:
    """Given: a minimal function declaration -- params and a single expr body."""

    __slots__ = ("params", "body")

    def __init__(self, params: List[str], body) -> None:
        self.params = params
        self.body = body


def evaluate(node, env: Environment):
    """Given: evaluate a PA3 expression AST node against `env` (Cells are transparently dereferenced)."""
    if isinstance(node, Number):
        return node.value
    if isinstance(node, Variable):
        val = env.resolve(node.name)
        return val.value if isinstance(val, Cell) else val
    if isinstance(node, BinOp):
        if node.op == "neg":
            return -evaluate(node.left, env)
        left = evaluate(node.left, env)
        right = evaluate(node.right, env)
        return {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b, "/": lambda a, b: a / b}[node.op](left, right)
    raise ValueError(f"cannot evaluate node: {node!r}")


def assign_through(env: Environment, name: str, value: Any) -> None:
    """Given: write `value` into whatever Cell `name` resolves to (mutates in place, does not rebind)."""
    cell = env.resolve(name)
    if not isinstance(cell, Cell):
        raise TypeError(f"'{name}' is not bound to a Cell -- did you forget to wrap it?")
    cell.value = value


def bind_parameters(
    param_specs: List[Tuple[str, str]],
    arg_nodes: list,
    caller_env: Environment,
    callee_record
) -> None:
    if len(param_specs) != len(arg_nodes):
        raise ValueError("Argument count must match parameter count.")

    callee_record.pending_writeback = []

    for (name, mode), arg_node in zip(param_specs, arg_nodes):
        if mode == "value":
            local_cell = Cell(evaluate(arg_node, caller_env))
            callee_record.locals_env.define(name, local_cell)

        elif mode in ("reference", "value-result"):
            if not isinstance(arg_node, Variable):
                raise TypeError(
                    f"Parameter '{name}' requires a variable argument."
                )

            caller_cell = caller_env.resolve(arg_node.name)

            if not isinstance(caller_cell, Cell):
                raise TypeError(
                    f"Argument '{arg_node.name}' must be stored in a Cell."
                )

            if mode == "reference":
                callee_record.locals_env.define(name, caller_cell)

            else:
                local_cell = Cell(caller_cell.value)
                callee_record.locals_env.define(name, local_cell)

                callee_record.pending_writeback.append(
                    (local_cell, caller_cell)
                )

        else:
            raise ValueError(f"Unknown parameter mode: '{mode}'")


def commit_value_result(callee_record, caller_env: Environment) -> None:
    for local_cell, caller_cell in callee_record.pending_writeback:
        caller_cell.value = local_cell.value

    callee_record.pending_writeback.clear()


class Closure:
    def __init__(self, declaration: FunctionDecl, defining_env: Environment) -> None:
        self.declaration = declaration
        self.defining_env = defining_env

    def call(self, args: list, caller_env: Environment):
        if len(args) != len(self.declaration.params):
            raise ValueError("Argument count must match parameter count.")

        callee_env = Environment(parent=self.defining_env)

        for name, value in zip(self.declaration.params, args):
            callee_env.define(name, Cell(value))

        return evaluate(self.declaration.body, callee_env)
