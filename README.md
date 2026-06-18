# MKotlin Compiler Project

A compiler implementation for **MKotlin**, a simple Kotlin-like programming language with complete type inference, built with the ANTLR4 parser generator.

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![ANTLR](https://img.shields.io/badge/ANTLR-4.13.2-orange.svg)](https://www.antlr.org/)
[![License](https://img.shields.io/badge/License-Academic-green.svg)](LICENSE)

## Overview

This is a mini project for the **Principles of Programming Languages** course that implements a compiler for **MKotlin**, a custom Kotlin-inspired language designed for educational purposes. The project follows a classic multi-phase pipeline (lexical analysis → parsing → AST generation → semantic analysis → code generation) and adopts Kotlin's surface syntax with a genuine `Boolean` type.

📋 **For the full language specification, see [MKotlin Specification](mkotlin_specification.md).**  
📋 **For AST node conventions (Assignment 2), see [AST Representation](mkotlin-ast_representation.md).**

The project demonstrates fundamental concepts of compiler construction:

- **Lexical Analysis**: tokenization and error handling (invalid characters, unclosed strings, illegal escapes).
- **Syntax Analysis**: grammar-based parsing with ANTLR4 — newline/semicolon statement separation, trailing type annotations, `when`, `data class`.
- **AST Generation**: building abstract syntax trees from parse trees.
- **Semantic Analysis**: complete local type inference with strict, deterministic type checking and a real `Boolean` type.
- **Code Generation**: generating target code (JVM via Jasmin) from the validated AST.
- **Error Handling**: comprehensive reporting across all phases.
- **Testing Framework**: automated testing with pytest.

### Language highlights

| Concern | MKotlin |
| --- | --- |
| Variable binding | `val` (immutable) / `var` (mutable) |
| Type annotation | trailing (`x: Int`) |
| Function | `fun f(...): Int { }` |
| Composite type | `data class` |
| Multi-way branch | `when` (no fall-through) |
| Booleans | true `Boolean` type |
| Statement end | newline; `;` optional |
| For loop | `for (i in a..b)` range |
| Data class equality | structural `==` |

---

## Assignment 1 — Lexical and Syntax Analysis

### Required Tasks to Complete

1. **Read the language specification carefully** — study [MKotlin Specification](mkotlin_specification.md); master the lexical and syntax rules (note: statements end at newlines; semicolons are optional).
2. **Implement `src/grammar/MKotlin.g4`** — complete the ANTLR4 grammar file; define lexer rules (tokens) and parser rules; handle precedence and associativity per the specification.
3. **Write 100 lexer tests** in `tests/test_lexer.py` and **100 parser tests** in `tests/test_parser.py` — valid/invalid tokens, error handling (unclosed strings, illegal escapes, underscores in numeric literals), nested structures, complex expressions, `when`/`data class`/`for-in-range`.

### Lexical Error Handling Requirements

- **ERROR_TOKEN** with `<unrecognized char>` lexeme — unrecognized character.
- **UNCLOSE_STRING** with `<unclosed string>` lexeme — unterminated string (lexeme excludes the opening quote).
- **ILLEGAL_ESCAPE** with `<wrong string>` lexeme — illegal escape; the wrong string runs from the start of the string (without the opening quote) to the illegal escape. Recall the supported escapes are `b f r n t " \ $`.

### Evaluation Criteria

- **Grammar Implementation**: Accuracy and completeness of `MKotlin.g4`.
- **Test Coverage**: Quantity and quality of the 200 test cases.
- **Error Handling**: Capability to handle lexical and syntax errors.

---

## Assignment 2 — AST Generation

### Required Tasks to Complete

1. **Study the AST node classes** in `src/utils/nodes.py` and the [AST Representation](mkotlin-ast_representation.md) document — understand the node hierarchy and how each MKotlin construct maps to a node.
2. **Implement `ASTGeneration`** in `src/astgen/ast_generation.py` — inherit from the generated `MKotlinVisitor`, override visit methods to build AST nodes, and cover every construct in the specification.
3. **Write AST tests** in `tests/test_ast_gen.py` — verify node types and structure for all features, including edge and nested cases. See [AST Representation](mkotlin-ast_representation.md) for `repr()` conventions (`VarDecl`, `ExprStmt`, `WhenBranch`, etc.).

### Requirements

The `ASTGeneration` class must inherit from `MKotlinVisitor`, return appropriate node objects from `nodes.py`, support all language features, and preserve the program's logical structure.

---

## Assignment 3 — Static Semantic Analysis

### Required Tasks to Complete

1. **Study the semantic rules** in [Semantic Constraints and Errors](mkotlin-semantic_constraints_and_errors.md).
2. **Implement `StaticChecker`** in `src/semantics/static_checker.py` — inherit from `ASTVisitor`; handle scope management, type inference for un-annotated `val`/`var` and inferred return types, type checking, and error detection.
3. **Write 100 checker tests** in `tests/test_checker.py` — cover all error types, valid programs, and edge cases; assert the **exact** first-error message (see [Semantic Constraints](mkotlin-semantic_constraints_and_errors.md) for `repr(node)` conventions).

### Error Types to Detect

1. **Redeclared** — duplicate variable / parameter / function / data class / loop variable / member.
2. **UndeclaredIdentifier** — use of an undeclared variable, parameter, or loop variable.
3. **UndeclaredFunction** — call to an undeclared function.
4. **UndeclaredClass** — use of an undeclared data class type.
5. **TypeCannotBeInferred** — an un-annotated `var` (or inferred return) whose type cannot be locally determined.
6. **TypeMismatchInStatement** — non-`Boolean` condition, bad range bounds, return mismatch, assignment/declaration mismatch, reassigning a `val`.
7. **TypeMismatchInExpression** — operator/operand mismatch, bad equality, `when` label mismatch, bad call arguments, invalid member access.
8. **MustInLoop** — `break`/`continue` outside a loop (`when` does not count).

### Evaluation Criteria

- Correctness and completeness of `StaticChecker`.
- Accurate local type inference (`val`/`var` and inferred return types).
- Accurate detection of all eight error types.
- Quality and coverage of the 100 test cases.

---

## Assignment 4 — Code Generation

### Required Tasks to Complete

1. **Study the codegen components** in `src/codegen/` and the runtime in `src/runtime/` (`io.java`, `jasmin.jar`); understand the flow `AST -> .j -> .class -> run on JVM`.
2. **Implement `CodeGenerator`** (`src/codegen/codegen.py`) — traverse the AST and emit Jasmin using the provided `Emitter`, `jasmin_code.py`, `utils.py`, and `io.py`; support data classes, `when`, range `for`, and short-circuit `&&`/`||`.
3. **Write 100 codegen tests** in `tests/test_codegen.py` — verify the output of generated programs across basic and advanced constructs.

### Requirements

Traverse the AST with `ASTVisitor`; generate valid, assembling-and-running Jasmin; support the built-in I/O functions through the runtime `io` class; manage the operand stack, local variables, and labels correctly.

### Evaluation Criteria

- Correctness and completeness of `CodeGenerator`.
- Proper use of the provided `Emitter` / runtime helpers.
- Generated code assembles and runs correctly on the JVM.
- Quality and coverage of the codegen tests.
- Program outputs match expected results.

---

## Project Structure

```
.
├── Makefile
├── run.py
├── README.md
├── requirements.txt
├── .gitignore
├── mkotlin_specification.md
├── mkotlin-ast_representation.md
├── mkotlin-semantic_constraints_and_errors.md
├── external/              # ANTLR jar (downloaded by `run.py setup`)
├── src/
│   ├── astgen/
│   │   └── ast_generation.py      # ASTGeneration — student implementation
│   ├── grammar/
│   │   ├── MKotlin.g4             # ANTLR4 grammar — student implementation
│   │   └── lexererr.py
│   ├── utils/
│   │   ├── error_listener.py
│   │   ├── nodes.py               # AST node definitions
│   │   └── visitor.py
│   ├── semantics/
│   │   ├── static_checker.py      # StaticChecker — student implementation
│   │   └── static_error.py        # the 8 error classes
│   ├── codegen/
│   │   ├── codegen.py             # CodeGenerator — student implementation
│   │   ├── emitter.py             # Emitter helpers (provided)
│   │   ├── jasmin_code.py         # Low-level Jasmin strings (provided)
│   │   ├── utils.py               # Symbol, Access, FunctionType (provided)
│   │   ├── io.py                  # Built-in I/O symbols (provided)
│   │   ├── error.py               # Codegen exceptions (provided)
│   │   └── frame.py
│   └── runtime/
│       ├── io.java                # runtime I/O for generated code
│       └── jasmin.jar             # Jasmin assembler (bundled)
├── tests/
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_ast_gen.py
│   ├── test_checker.py
│   ├── test_codegen.py
│   └── utils.py
```

## Quick Start

### Prerequisites

- **Python 3.12+** (recommended) or Python 3.8+
- **Java Runtime Environment (JRE) 8+** (required for ANTLR4, Jasmin assembly, and running generated programs)

### Setup

```bash
python3 run.py check
python3 run.py setup    # creates venv, downloads ANTLR, installs dependencies
python3 run.py build
```

`setup` downloads the ANTLR jar into `external/` and installs Python packages into `venv/`. Tests always run through the project virtual environment (`venv/Scripts/python.exe -m pytest` on Windows), so you do not need to activate the venv manually.

On Windows, if `python3` is not available, use `py run.py setup` instead. If `pytest --version` works but `python3 run.py test-lexer` fails, the global `pytest` command is tied to a different Python — always use `python3 run.py test-*` (or `py run.py test-*`).

### Run tests

```bash
python3 run.py test-lexer
python3 run.py test-parser
python3 run.py test-ast
python3 run.py test-checker
python3 run.py test-codegen
```

## License

Developed for educational purposes as part of the **Principles of Programming Languages** course by MEng. Trần Ngọc Bảo Duy (Faculty of Computer Science and Engineering, HCMUT, VNU-HCM).
