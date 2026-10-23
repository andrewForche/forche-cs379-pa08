from dataclasses import dataclass, field
from typing import List

from lexer import Token, tokenize


@dataclass
class Program:
    statements: list


@dataclass
class Declaration:
    name: str
    expr: object
    line: int


@dataclass
class Assignment:
    name: str
    expr: object
    line: int


@dataclass
class BinOp:
    op: str
    left: object
    right: object
    line: int


@dataclass
class Number:
    value: int
    line: int


@dataclass
class Variable:
    name: str
    line: int


class ParseError(Exception):
    pass


class _ParserState:
    """Given: a small cursor wrapper over the token list. Not required to use, but handy."""

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.pos = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def advance(self) -> Token:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def expect(self, type_: str) -> Token:
        tok = self.peek()
        if tok.type != type_:
            raise ParseError(f"Line {tok.line}: expected {type_}, found {tok.type} ({tok.lexeme!r}).")
        return self.advance()


def parse_factor(state: _ParserState):
    tok = state.peek()

    if tok.type == "NUMBER":
        state.advance()
        return Number(value=int(tok.lexeme), line=tok.line)

    if tok.type == "IDENT":
        state.advance()
        return Variable(name=tok.lexeme, line=tok.line)

    if tok.type == "LPAREN":
        state.advance()
        expr = parse_expr(state)
        state.expect("RPAREN")
        return expr

    raise ParseError(
        f"Line {tok.line}: expected NUMBER, IDENT, or LPAREN, "
        f"found {tok.type} ({tok.lexeme!r})."
    )


def parse_term(state: _ParserState):
    left = parse_factor(state)

    while state.peek().type in ("STAR", "SLASH"):
        op = state.advance()
        right = parse_factor(state)

        left = BinOp(
            op=op.lexeme,
            left=left,
            right=right,
            line=op.line
        )

    return left


def parse_expr(state: _ParserState):
    left = parse_term(state)

    while state.peek().type in ("PLUS", "MINUS"):
        op = state.advance()
        right = parse_term(state)

        left = BinOp(
            op=op.lexeme,
            left=left,
            right=right,
            line=op.line
        )

    return left


def parse_declaration(state: _ParserState) -> Declaration:
    let_token = state.expect("LET")
    name_token = state.expect("IDENT")
    state.expect("ASSIGN")

    expr = parse_expr(state)

    state.expect("SEMI")

    return Declaration(
        name=name_token.lexeme,
        expr=expr,
        line=let_token.line
    )


def parse_assignment(state: _ParserState) -> Assignment:
    name_token = state.expect("IDENT")
    state.expect("ASSIGN")

    expr = parse_expr(state)

    state.expect("SEMI")

    return Assignment(
        name=name_token.lexeme,
        expr=expr,
        line=name_token.line
    )


def parse_statement(state: _ParserState):
    tok = state.peek()

    if tok.type == "LET":
        return parse_declaration(state)

    if tok.type == "IDENT":
        return parse_assignment(state)

    raise ParseError(
        f"Line {tok.line}: expected LET or IDENT, "
        f"found {tok.type} ({tok.lexeme!r})."
    )


def parse_program(state: _ParserState) -> Program:
    statements = []

    while state.peek().type != "EOF":
        statements.append(parse_statement(state))

    state.expect("EOF")
    return Program(statements=statements)


def parse(tokens: List[Token]) -> Program:
    state = _ParserState(tokens)
    return parse_program(state)
