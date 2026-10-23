import re
from dataclasses import dataclass


@dataclass
class Token:
    type: str
    lexeme: str
    line: int


class LexError(Exception):
    pass


KEYWORDS = {"let"}

MASTER_PATTERN = re.compile(
    r"(?P<NUMBER>[0-9]+(\.[0-9]+)?)"
    r"|(?P<IDENT>[a-zA-Z_][a-zA-Z0-9_]*)"
    r"|(?P<PLUS>\+)|(?P<MINUS>-)|(?P<STAR>\*)|(?P<SLASH>/)"
    r"|(?P<LPAREN>\()|(?P<RPAREN>\))|(?P<ASSIGN>=)|(?P<SEMI>;)"
    r"|(?P<COMMENT>#.*)|(?P<NEWLINE>\n)|(?P<SKIP>[ \t]+)|(?P<MISMATCH>.)"
)


def tokenize(source: str) -> list[Token]:
    tokens = []
    line = 1
    pos = 0

    while pos < len(source):
        m = MASTER_PATTERN.match(source, pos)
        kind, lexeme = m.lastgroup, m.group()

        if kind == "NEWLINE":
            line += 1
        elif kind in ("SKIP", "COMMENT"):
            pass
        elif kind == "MISMATCH":
            raise LexError(f"Unexpected char {lexeme!r} at line {line}")
        elif kind == "IDENT" and lexeme in KEYWORDS:
            tokens.append(Token("LET", lexeme, line))
        else:
            tokens.append(Token(kind, lexeme, line))

        pos = m.end()

    tokens.append(Token("EOF", "", line))
    return tokens