"""Error classes for code generation."""


class IllegalOperandException(Exception):
    """Exception for illegal operands in code generation."""

    def __init__(self, msg):
        self.s = msg

    def __str__(self):
        return "Illegal Operand: " + self.s + "\n"
