# MKotlin Programming Language — Semantic Constraints and Error Types

**Version 1.1 - July 2026**

This document defines the static semantic constraints checked by the MKotlin compiler in **Assignment 3 (Static Semantic Analysis)**, and the exact error types your `StaticChecker` must raise. It complements the [MKotlin Specification](mkotlin_specification.md) and the [AST Representation](mkotlin-ast_representation.md) document; read them together.

The checker traverses the AST (produced in Assignment 2) using the visitor pattern, manages scopes, infers types for un-annotated `val`/`var` bindings and inferred return types, and reports the **first** error it encounters by raising the corresponding exception. If a program is well-formed, the checker returns normally (no exception).

---

## Table of Contents

1. [General Principles](#general-principles)
2. [Scope and Environment Model](#scope-and-environment-model)
3. [Error Types](#error-types)
4. [Detailed Constraints by Construct](#detailed-constraints-by-construct)
5. [Type Inference Obligations](#type-inference-obligations)
6. [Worked Examples](#worked-examples)

---

## General Principles

- **Single error reporting.** The checker raises an exception for the **first** violation found, in a deterministic traversal order (declarations top-to-bottom; within a body, statements in source order; within an expression, left-to-right, operator after operands). Tests rely on this order.
- **Declared-before-use.** Functions, data classes (as types and as constructors), variables, parameters, and loop variables must be declared before they are used in source-text order, subject to the scope rules below.
- **No overloading / unique names.** Function names are globally unique; data class names are globally unique; the built-in I/O functions occupy reserved names (see below).
- **Built-in functions.** `readInt`, `readFloat`, `readBool`, `readString`, `printInt`, `printFloat`, `printBool`, `printString` are predeclared in the global environment with the prototypes in the specification. A user declaration that reuses one of these names is a `Redeclared` function.
- **`Unit` placement.** `Unit` may appear only as a function return type. Using `Unit` as a parameter type, variable type, or data class member type is a `TypeMismatchInStatement` (for declarations) / structural error as specified per construct below.

---

## Scope and Environment Model

The environment is a stack of scopes:

- **Global scope:** all function and data class names (including built-ins).
- **Function scope:** the parameters of the function, plus the top-level declarations of the body.
- **Block / control scopes:** each block `{ ... }` and each `when`/`if`/`while` body introduces a nested scope per the specification. A `for` introduces a loop-variable scope nested under the enclosing scope, and its body is checked in a further inner scope nested under the loop-variable scope.

Resolution searches innermost-to-outermost. Shadowing an **outer** local in an **inner** scope is permitted. Re-declaring a name **in the same scope** is a `Redeclared` error. Reusing a parameter name as a top-level body variable (same scope as parameters) is `Redeclared`.

The initializer of a declaration is checked in the scope **before** the new name is added (the name is not in scope of its own initializer).

---

## Error Types

Your `StaticChecker` must detect exactly these eight error types. Each corresponds to an exception class in `src/semantics/static_error.py`.

1. **Redeclared** — A variable, parameter, function, data class, or data class member is declared more than once in a scope where that is not allowed. Carries the kind (Variable / Parameter / Function / Class / Constant / Member) and the offending name.

2. **UndeclaredIdentifier** — Use of a variable, parameter, or loop variable that is not in scope.

3. **UndeclaredFunction** — A call `f(args)` where `f` resolves to neither a declared (or built-in) function nor a declared data class. A call whose name is completely unknown is treated as an unknown function call.

4. **UndeclaredClass** — Use of an undeclared data class name in a type position (a variable annotation, parameter type, return type, or member type).

5. **TypeCannotBeInferred** — An un-annotated `var` (or inferred return type) whose type cannot be determined from its first usage under the local inference rules. The argument is the AST node where inference fails; tests expect `Type Cannot Be Inferred: ` + `repr(node)` (e.g. `BinaryOp(*, Id(a), Id(b))` for `val c = a * b` when both operands are unknown).

6. **TypeMismatchInStatement** — A type incompatibility in a statement (`if`/`while`/`for` condition not `Boolean`, bad range bounds, `return` mismatch, assignment mismatch, reassigning a `val`, etc.). The argument is the offending **statement** node; tests expect `Type Mismatch In Statement: ` + `repr(node)` (e.g. `Assign(Id(x), IntLit(2))` or `While(Id(i), Block(...))`).

7. **TypeMismatchInExpression** — A type incompatibility within an expression (operator operands, equality, `when` labels, call arguments, member access, etc.). The argument is the offending **expression** node; tests expect `Type Mismatch In Expression: ` + `repr(node)` (e.g. `BinaryOp(&&, BoolLit(true), IntLit(1))`).

8. **MustInLoop** — A `break` or `continue` outside a `while`/`for` loop (`when` does not count). The argument is the `Break()` or `Continue()` node; tests expect `Must In Loop: Break()` (or `Continue()`).

---

## Detailed Constraints by Construct

### Program

- A program with no `main` function is still type-checked; the absence of `main` is not itself a static error in Version 1.0 (it would be a link/run error). Tests focus on the eight error types above.
- Data class and function declarations are processed top-to-bottom for the declared-before-use rule.

### Data Class Declaration

- The data class name must be unique among data classes and not collide with a function name → else `Redeclared(Class, name)`.
- Member names must be unique within the data class → else `Redeclared(Member, name)`.
- Each member type must be `Int`, `Float`, `Boolean`, `String`, or a **previously declared** data class type. An undeclared type name → `UndeclaredClass(name)`. `Unit` as a member type → `TypeMismatchInStatement` on the member.
- A member type may not be the data class currently being defined (it is not yet "declared" for its own members) → `UndeclaredClass(name)`.

### Function Declaration

- The function name must be unique among functions, data classes, and built-ins → else `Redeclared(Function, name)`.
- Parameter names must be unique within the parameter list → else `Redeclared(Parameter, name)`.
- Each parameter type must be a declared type; `Unit` is not allowed as a parameter type.
- The body is checked in a scope containing the parameters. A top-level body declaration reusing a parameter name → `Redeclared`.
- If the return type is omitted, it is inferred per Rule 5; inconsistent `return` types → `TypeMismatchInStatement`; if no usage determines it and it is not `Unit`, the relevant `return` triggers the mismatch.

### Variable Declaration

- A `val` requires an initializer; a `val` without one is a structural error surfaced as `TypeCannotBeInferred` on the declaration (there is nothing to infer from and reassignment is forbidden).
- A redeclaration in the same scope → `Redeclared(Variable, name)` (or `Constant` for a `val`, if your error classes distinguish; otherwise `Variable`).
- With an explicit annotation `T` and an initializer `e`: `type(e)` must match `T` (with `Int → Float` widening) → else `TypeMismatchInStatement`. An undeclared `T` → `UndeclaredClass`.
- With inference (no annotation), see [Type Inference Obligations](#type-inference-obligations).

### Assignment

- The target must be assignable: a `var` variable, an explicitly-typed-or-inferred mutable binding, or a member access rooted at a `var`. Assigning to a `val` (or to a member rooted at a `val`) → `TypeMismatchInStatement`.
- The value type must match the target type (with `Int → Float` widening) → else `TypeMismatchInStatement`.
- Using an undeclared target identifier → `UndeclaredIdentifier`.

### If / While

- The condition must be `Boolean` → else `TypeMismatchInStatement`.
- Branch/body statements are checked in nested scopes.

### For

- The range `a..b` requires `type(a)` and `type(b)` to be `Int` → else `TypeMismatchInStatement`.
- The loop variable is an immutable `Int` in scope only within the loop construct (header and body). Assigning to it inside the body → `TypeMismatchInStatement`.
- The body is checked in a scope nested under the loop-variable scope. A declaration in the body may therefore shadow the loop variable and is not a `Redeclared` error.

### When

- **Subject form:** `type(subject)` must be comparable (`Int`, `Float`, `Boolean`, `String`). Each label expression must match the subject type (with `Int`/`Float` promotion) → else `TypeMismatchInExpression`. More than one `else` → `Redeclared`-style structural error reported as `TypeMismatchInStatement` (implementations may instead reject at parse time; if it reaches the checker, raise `TypeMismatchInStatement`).
- **Conditionless form:** each guard must be `Boolean` → else `TypeMismatchInExpression`.
- As an **expression**, every branch must yield the same type and an `else` is required → else `TypeMismatchInExpression`.

### Break / Continue

- Must be lexically inside a `while` or `for` → else `MustInLoop`.

### Return

- In a `Unit` function (declared or inferred): `return` with a value → `TypeMismatchInStatement`.
- In a non-`Unit` function: `return` without a value, or with a value of the wrong type → `TypeMismatchInStatement`.

### Expressions

- **Identifiers:** undeclared variable/parameter/loop variable → `UndeclaredIdentifier`.
- **Calls `f(args)`:** resolve `f` against declared functions and data classes. A declared function produces a function call; a declared data class produces a constructor call; if neither declaration exists → `UndeclaredFunction`. Wrong argument count or types for either kind of resolved call → `TypeMismatchInExpression`. Resolution is based on declarations, not identifier capitalization.
- **Member access `e.m`:** `type(e)` must be a data class type → else `TypeMismatchInExpression`; `m` must be a member of that data class → else `TypeMismatchInExpression`.
- **Operators:** operand types must satisfy the operator's rules (see specification) → else `TypeMismatchInExpression`.
- **Increment/decrement:** operand must be an assignable `Int` target → else `TypeMismatchInExpression` (wrong type) or `TypeMismatchInStatement` (assigning a `val`/loop variable), per the offending condition.

---

## Type Inference Obligations

Inference is **local** and **deterministic**, matching the specification:

- `val v = e` / `var v = e`: `type(v) = type(e)`.
- `var v` (no annotation, no initializer): infer from first usage —
  - assignment `v = rhs` → `type(v) = type(rhs)`;
  - whole-argument position `f(v)` → `type(v) = parameter type`;
  - whole-return position `return v` → `type(v) = function return type`;
  - otherwise → `TypeCannotBeInferred(node)`.
- **Integer-literal anchor:** in `+ - * /`, an undetermined `var` opposite an integer literal is fixed to `Int`.
- **No deep propagation:** an explicit target/annotation/parameter type does not recursively assign types to multiple un-annotated `var`s nested inside a compound expression. If two unknowns appear with no anchor, that is `TypeCannotBeInferred`.
- **Inferred return type:** the type of the first value-returning `return`; `Unit` if none. Later inconsistent returns → `TypeMismatchInStatement`.

---

## Worked Examples

**Redeclared (parameter vs. body variable):**

    fun f(x: Int) {
        val x = 5     // Redeclared(Variable, x) — same scope as parameter x
    }

**UndeclaredIdentifier:**

    fun main() {
        printInt(y)   // UndeclaredIdentifier(y)
    }

**UndeclaredFunction / UndeclaredClass:**

    fun main() {
        val a = compute(3)    // UndeclaredFunction(compute)
        var p: Vec            // UndeclaredClass(Vec) — type position
    }

**TypeMismatchInStatement (condition not Boolean):**

    fun main() {
        var i = 0
        while (i) {           // TypeMismatchInStatement — Int is not Boolean
            i++
        }
    }

**TypeMismatchInStatement (reassign a val):**

    fun main() {
        val x = 1
        x = 2                 // TypeMismatchInStatement — cannot reassign val
    }

**TypeMismatchInExpression (operator operand types):**

    fun main() {
        val b = true && 1     // TypeMismatchInExpression — && needs Boolean
    }

**TypeCannotBeInferred:**

    fun main() {
        var a
        var b
        val c = a * b         // TypeCannotBeInferred — two unknowns, no anchor
    }

**MustInLoop:**

    fun main() {
        when (1) {
            1 -> break        // MustInLoop — when is not a loop
            else -> printInt(0)
        }
    }

---

**End of Semantic Constraints and Error Types**
