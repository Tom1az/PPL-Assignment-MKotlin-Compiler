# MKotlin Programming Language — AST Representation

**Version 1.0 - June 2026**

This document defines how MKotlin source constructs map to AST nodes for **Assignment 2 (AST Generation)**. The node classes live in `src/utils/nodes.py`. AST-generation tests compare `repr()` of the generated tree against expected strings using the conventions below.

Read this together with the [MKotlin Specification](mkotlin_specification.md) for language syntax and semantics.

---

## Table of Contents

1. [General Rules](#general-rules)
2. [VarDecl Representation](#vardecl-representation)
3. [ExprStmt (Expression Statements)](#exprstmt-expression-statements)
4. [WhenBranch.body by Context](#whenbranchbody-by-context)
5. [Types in the AST](#types-in-the-ast)
6. [Node Hierarchy Summary](#node-hierarchy-summary)

---

## General Rules

- **Parenthesized expressions** are not wrapped in a dedicated node; unwrap to the inner expression (e.g. `(1 + 2)` becomes `BinaryOp("+", IntLit(1), IntLit(2))`).
- **Function calls** and **constructor calls** both become `CallExpr(name, [args…])`; the static checker (Assignment 3) decides whether `name` is a function or a data class.
- **Assignment** appears as `Assign(lhs, rhs)` in statement position and `AssignExpr(lhs, rhs)` in expression position (including chained assignments such as `x = y = z = 10`).

---

## VarDecl Representation

A `val` / `var` declaration becomes `VarDecl(name, mutable, declared_type, init)`:

| Field | Meaning |
| --- | --- |
| `name` | Identifier |
| `mutable` | `False` for `val`, `True` for `var` |
| `declared_type` | Explicit type node, or `None` when inferred |
| `init` | Initializer expression, or `None` when absent |

The `repr()` format uses the keyword as the first argument (not the boolean flag):

    VarDecl(val, x, None, IntLit(10))      // val x = 10
    VarDecl(var, count, IntType(), None)   // var count: Int

---

## ExprStmt (Expression Statements)

Statements that are expressions for their side effects must be wrapped in `ExprStmt`, not placed bare in a `Block`:

    fun main() {
        printInt(42)     // statement position
    }

becomes:

    ExprStmt(CallExpr("printInt", [IntLit(42)]))

The same applies to assignment statements used as standalone statements, postfix/prefix increment used as statements, and any other expression used where a statement is required.

**Do not** wrap the initializer of a `val`/`var` declaration in `ExprStmt`; the initializer is stored directly in `VarDecl.init`.

---

## WhenBranch.body by Context

`WhenBranch` is shared by `When` (statement) and `WhenExpr` (expression). The `body` field type depends on which form produced the branch:

| Context | `WhenBranch.body` must be |
| --- | --- |
| `when { … }` statement | A `Stmt` — typically `Block(…)` or `ExprStmt(…)` for a single call/assignment |
| `when { … }` expression | An `Expr` — the value produced by that branch |

The `else` branch uses `labels = None`; `repr()` shows `WhenBranch(else, body)`.

Example (statement form):

    when (day) {
        1 -> printInt(1)
        else -> printInt(0)
    }

Each `->` right-hand side is a **statement**; a lone function call becomes `ExprStmt(CallExpr(…))`, not a bare `CallExpr`.

---

## Types in the AST

Source types map to nodes as follows: `Int` → `IntType()`, `Float` → `FloatType()`, `Boolean` → `BoolType()`, `String` → `StringType()`, `Unit` → `UnitType()`, and a data class name `C` → `ClassType(C)`.

Function return types omitted in source are represented as `return_type = None` on `FuncDecl` until your generator chooses to record an inferred type explicitly (tests accept `None` for `fun main() { … }` without an annotation).

---

## Node Hierarchy Summary

    Program
      ├── decls: list[Decl]            (DataClassDecl | FuncDecl)

    Types        : IntType, FloatType, BoolType, StringType, UnitType, ClassType
    Declarations : DataClassDecl, MemberDecl, FuncDecl, Param, VarDecl
    Statements   : Block, If, While, For, When, Break, Continue, Return,
                   Assign, ExprStmt
    Expressions  : BinaryOp, UnaryOp, PostfixOp, AssignExpr, CallExpr, MemberAccess,
                   IfExpr, WhenExpr, Id, IntLit, FloatLit, BoolLit, StringLit

Implement `ASTGeneration` in `src/astgen/ast_generation.py` by overriding the ANTLR visitor methods to build these nodes from the parse tree.

---

**End of AST Representation**
