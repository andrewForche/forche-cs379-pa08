from typing import Optional

from parser import Assignment, BinOp, Declaration, Number, Program, Variable


class SemanticError(Exception):
    pass


class Environment:
    def __init__(self, parent: "Environment | None" = None):
        self.parent = parent
        self._names: dict[str, int] = {}

    def define(self, name: str, line: int) -> None:
        if name in self._names:
            original_line = self._names[name]
            raise SemanticError(
                f"Duplicate declaration of '{name}' "
                f"(line {line}; originally declared line {original_line})."
            )

        self._names[name] = line

    def resolve(self, name: str) -> int:
        scope = self

        while scope is not None:
            if name in scope._names:
                return scope._names[name]

            scope = scope.parent

        raise SemanticError(
            f"Use of undeclared variable '{name}'."
        )


def check_program(ast: Program) -> Environment:
    env = Environment()

    def check_expr(expr):
        if isinstance(expr, Number):
            return

        elif isinstance(expr, Variable):
            try:
                env.resolve(expr.name)
            except SemanticError:
                raise SemanticError(
                    f"Use of undeclared variable '{expr.name}' "
                    f"(line {expr.line})."
                ) from None

        elif isinstance(expr, BinOp):
            check_expr(expr.left)
            check_expr(expr.right)

        else:
            raise TypeError(
                f"Unsupported expression node: {type(expr).__name__}"
            )

    for statement in ast.statements:
        if isinstance(statement, Declaration):
            check_expr(statement.expr)
            env.define(statement.name, statement.line)

        elif isinstance(statement, Assignment):
            try:
                env.resolve(statement.name)
            except SemanticError:
                raise SemanticError(
                    f"Use of undeclared variable '{statement.name}' "
                    f"(line {statement.line})."
                ) from None

            check_expr(statement.expr)

        else:
            raise TypeError(
                f"Unsupported statement node: "
                f"{type(statement).__name__}"
            )

    return env
