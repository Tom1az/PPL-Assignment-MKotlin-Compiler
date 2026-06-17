"""ANTLR error listeners for the MKotlin compiler.

``NewErrorListener`` raises a ``SyntaxException`` on the first parser error so
that parser tests can assert on syntax errors.  The lexer error listener is
kept minimal because lexical errors are surfaced through the custom
``lexererr`` exceptions raised inside the grammar actions.
"""

from antlr4.error.ErrorListener import ErrorListener


class SyntaxException(Exception):
    def __init__(self, msg):
        super().__init__(msg)
        self.message = msg


class NewErrorListener(ErrorListener):
    INSTANCE = None

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        raise SyntaxException(
            f"Error on line {line} col {column}: {offendingSymbol.text}"
            if offendingSymbol is not None
            else f"Error on line {line} col {column}: {msg}"
        )


NewErrorListener.INSTANCE = NewErrorListener()
