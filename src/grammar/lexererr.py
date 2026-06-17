"""Custom lexer error classes for the MKotlin compiler.

These mirror the error-token conventions described in the language
specification.  When the lexer detects a problem it raises one of these
exceptions carrying the offending lexeme; the error listener turns the
exception into a token with the appropriate type and lexeme.
"""


class LexerError(Exception):
    """Base class for all lexer errors."""

    def __init__(self, message: str = ""):
        super().__init__(message)
        self.message = message


class ErrorToken(LexerError):
    """Raised when the lexer meets an unrecognized character."""

    def __init__(self, char: str):
        super().__init__(char)
        self.char = char


class UncloseString(LexerError):
    """Raised when a string literal is not closed.

    ``literal`` holds the string content *without* the opening quote and
    *without* the terminating newline / carriage return.
    """

    def __init__(self, literal: str):
        super().__init__(literal)
        self.literal = literal


class IllegalEscape(LexerError):
    """Raised when a string literal contains an illegal escape sequence.

    ``literal`` holds the string content from the start (without the opening
    quote) up to and including the illegal escape sequence.
    """

    def __init__(self, literal: str):
        super().__init__(literal)
        self.literal = literal
