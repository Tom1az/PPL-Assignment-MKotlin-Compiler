# MKotlin Programming Language Specification

**Version 1.2 - August 2026**

## Table of Contents

1. [Introduction](#introduction)
2. [Program Structure](#program-structure)
3. [Lexical Structure](#lexical-structure)
4. [Type System](#type-system)
5. [Expressions](#expressions)
6. [Statements](#statements)
7. [Type Inference](#type-inference)
8. [Scope Rules](#scope-rules)
9. [Input and Output](#input-and-output)
10. [Example Programs](#example-programs)

---

## Introduction

**MKotlin**, pronounced "mini-Kotlin", is a simple Kotlin-like programming language designed primarily for students practicing implementing a simple compiler. MKotlin borrows the surface syntax and a few signature features of Kotlin — `val`/`var` declarations, trailing type annotations, `fun` functions, `data class`, and the `when` expression — while keeping the type system small and the type-checking rules deterministic.

MKotlin features a complete type inference system with strict type checking. Each operator has well-defined type requirements, so type checking is straightforward while preserving Kotlin-like syntax. Unlike the C family, MKotlin has a genuine `Boolean` type: conditions in `if`, `while`, and `for` must be `Boolean`, not an integer used as a truth value.

Despite its simplicity, MKotlin includes most important features of a procedural programming language such as functions, immutable and mutable variables, control flow structures (`if`, `while`, `for`, `when`), and complete type inference.

---

## Program Structure

For simplicity, an MKotlin compiler does not support compiling multiple files, so an MKotlin program is written in a single file. An MKotlin program consists of a (possibly empty) sequence of **data class declarations** and **function declarations**, in any order subject to the declared-before-use rule in [Scope Rules](#scope-rules). Consecutive top-level declarations must be separated by at least one **separator** (a newline or semicolon); see [Separators and Statement/Declaration Lists](#separators-and-statementdeclaration-lists).

The entry point of an MKotlin program is a function named `main` that takes no parameters and returns `Unit`. Each such function in an MKotlin program is an entry point of the program.

### Function Declaration

A function declaration has the following form:

    fun <identifier>(<parameter_list>): <return_type> {
        <statement_list>
    }

Where:

- `fun` is the keyword that introduces a function.
- `<identifier>` is the function name.
- `<parameter_list>` is a comma-separated list of parameter declarations (or empty).
- `<return_type>` is a type which is described in Section 4. The return type annotation `: <return_type>` is **optional**; when omitted, the return type is inferred (see [Type Inference](#type-inference)).
- `<statement_list>` is a (possibly empty) sequence of statements, as defined in [Statements](#statements).

A parameter declaration has the form:

    <identifier>: <type>

where `<identifier>` is the parameter name and `<type>` must be an explicit type (`Int`, `Float`, `Boolean`, `String`, or a data class type name). **Note:** Parameters always require an explicit type annotation — they cannot be inferred.

**Function Overloading:** MKotlin does not support function overloading. In an MKotlin program, function names must be unique — there cannot be two functions with the same name, regardless of their parameter types or return types. This restriction simplifies type inference, as the type of a function call can be determined solely by the function name.

#### Example

    fun add(x: Int, y: Int): Int {
        return x + y
    }

    fun main(): Unit {
        val result = add(3, 5)
        printInt(result)
    }

#### Example with Inferred Return Type

When the return type annotation is omitted, it is inferred from the `return` statements in the function:

    // Return type inferred as Int
    fun add(x: Int, y: Int) {
        return x + y
    }

    // Return type inferred as Float
    fun multiply(a: Float, b: Float) {
        return a * b
    }

    // Return type inferred as Unit (no value-returning return statement)
    fun greet(name: String) {
        printString("Hello, ")
        printString(name)
    }

    fun main() {
        val sum = add(3, 5)               // sum: Int
        val product = multiply(2.5, 3.0)  // product: Float
        greet("World")
    }

---

## Lexical Structure

### Character Set

The character set of MKotlin is extended ASCII (characters with code points 0–255). Blank (`' '`), tab (`'\t'`), form feed (the ASCII FF, `'\f'`), carriage return (the ASCII CR, `'\r'`) and newline (the ASCII LF, `'\n'`) are whitespace characters. The `'\n'` is used as the newline character in MKotlin.

Although newline is listed among whitespace characters for line-numbering purposes, the parser treats `NEWLINE` as a **significant token** (similar to Python), not as skippable layout in every context. Blank, tab, and form feed are insignificant and are skipped by the lexer; newline is not skipped globally and may appear only where the grammar allows it (see [Newlines and Layout](#newlines-and-layout)).

Carriage return (`\r`) is also listed as a whitespace character, but its lexical role differs by context: `\r` (or `\n`, or `\r\n` as a single line ending) terminates a line comment and triggers an unclosed-string error inside string literals; only `\n` (with an optional preceding `\r` in `\r\n`) forms the parser's `NEWLINE` token. A bare `\r` is not skipped like space or tab.

This definition of lines can be used to determine the line numbers produced by an MKotlin compiler.

### Statement Termination

Unlike many C-like languages, MKotlin statements are **not terminated by semicolons**. A statement ends at a newline (or at the natural end of the construct, such as a closing brace). A semicolon (`;`) is **optional** and may be used to write two statements on the same line; it is otherwise unnecessary. A semicolon by itself is not a valid statement.

For example, both of the following are valid:

    val x = 10
    val y = 20

    val x = 10; val y = 20

### Newlines and Layout

In MKotlin, newline (`\n`) is a **significant token** for the parser: it separates statements and may appear only where the grammar allows it. Space, tab, and form feed are insignificant and are skipped by the lexer.

A newline is **not** universal “insignificant whitespace” before `{`. Whether a newline may appear immediately before an opening brace depends on the construct:

| **Construct** | **Newline before `{`?** | **Example** |
| --- | --- | --- |
| Function body | **No** — `{` must follow `)` or `: <return_type>` on the same logical header | `fun main() { }` ✓; `fun main()\n{ }` ✗ |
| `if` / `while` / `for` body (block) | **Yes** — optional newlines may appear before the body `<statement>` | `if (a)\n{ ... }` ✓ |
| `when { ... }` | **No** — `{` must follow `when` or `when (<expr>)` directly | `when (x) { }` ✓; `when (x)\n{ }` ✗ |
| Block internals | **Yes** — `{` may be followed by newlines; statements inside are separated by newlines or `;` | `{\n  val x = 1\n}` ✓ |
| Empty parentheses `()` | **No** — `)` must follow `(` directly (only insignificant space/tab may appear inside) | `main()` ✓; `main(\n )` ✗ |

**Rule of thumb:** if the grammar expects a `<statement>` or `<block>` next, optional newlines are allowed; if it expects `{` as the immediate continuation of a declaration header (`fun ...`, `when ...`), or `)` immediately after `(` in an empty parameter/argument list, they are not.

For example:

    fun main() {
        printInt(1)
    }                          // valid

    fun main()
    {
        printInt(1)
    }                          // invalid: syntax error at newline before `{`

    if (a > 0) {
        printInt(1)
    }                          // valid

    if (a > 0)
    {
        printInt(1)
    }                          // valid

### Lexical Tokenization

This section clarifies how the lexer groups characters when multiple lexical rules could apply.

#### Range operator vs float literals

Both the range operator `..` and float literals such as `1.` and `.5` are valid in MKotlin. The lexer must recognize `..` as a single `RANGE` token **before** attempting to read a float literal whose trailing dot would consume the first dot of a range.

| **Input** | **Tokens** |
| --- | --- |
| `1..2` | `INTLIT(1)`, `RANGE(..)`, `INTLIT(2)` |
| `1....2` | `INTLIT(1)`, `RANGE(..)`, `RANGE(..)`, `INTLIT(2)` |

The tokenization `FLOATLIT(1.)`, `FLOATLIT(.2)` for `1..2` is **incorrect**.

**Implementation note:** define the `RANGE` (`'..'`) lexer rule before float rules that accept a trailing dot (`DIGITS '.'`), or use a semantic predicate so that `1.` is not recognized when the next character is another `.`.

#### Empty parentheses

Inside empty parameter or argument lists, only insignificant whitespace (space, tab, form feed) may appear between `(` and `)`. A `NEWLINE` there is a syntax error:

    fun main() { }              // valid
    fun main( ) { }             // valid (insignificant space only)
    fun main(
    ) { }                      // invalid
    getPoint(
    )                          // invalid

### Comment

There are two types of comment in MKotlin: block and line. A block comment starts with `"/*"` and ignores all characters (except EOF) until it reaches `"*/"`. A line comment ignores all characters from `"//"` to the end of the current line. **End of the current line** means the next `\n` or `\r` (including the `\r` in a Windows `\r\n` line ending).

For example:

    /* This is a block comment, that
    may span many lines */
    val x = 5 // this is a line comment

The following rules are enforced in MKotlin:

- Comments are not nested.
- `"/*"` and `"*/"` have no special meaning in any line comment.
- `"//"` has no special meaning in any block comment.
- An unclosed block comment at EOF (no closing `*/`) is **not** one of the three defined lexical errors. The `/* … */` lexer rule simply does not match; the lexer continues tokenizing the remaining source normally.

### Identifier

Identifiers are used to name variables, functions, parameters, data classes, and members. Identifiers begin with a letter (A–Z or a–z) or underscore (`_`), and may contain letters, underscores, and digits (0–9). MKotlin is case-sensitive, therefore the following identifiers are distinct: `MyVar`, `myvar`, and `MYVAR`.

### Keyword

The following character sequences are reserved as keywords and cannot be used as identifiers:

| **break** | **class** | **continue** | **data** | **else** | **false** |
| --- | --- | --- | --- | --- | --- |
| **for** | **fun** | **if** | **in** | **is** | **return** |
| **true** | **val** | **var** | **when** | **while** |  |

The following are reserved type names (built-in types) and likewise cannot be used as identifiers:

| **Int** | **Float** | **Boolean** | **String** | **Unit** |
| --- | --- | --- | --- | --- |

### Operator

The following is a list of **valid** operators along with their meaning. Note the applicable types for each operator:

| **Operator** | **Meaning** | **Applicable Type** |
| --- | --- | --- |
| `+` | Addition or unary plus | Int or Float |
| `-` | Subtraction or unary minus | Int or Float |
| `*` | Multiplication | Int or Float |
| `/` | Division | Int or Float |
| `%` | Modulus | Int only |
| `==` | Equal | Int, Float, Boolean, String, or same data class |
| `!=` | Not equal | Int, Float, Boolean, String, or same data class |
| `<` | Less than | Int or Float |
| `>` | Greater than | Int or Float |
| `<=` | Less than or equal | Int or Float |
| `>=` | Greater than or equal | Int or Float |
| `||` | Logical OR | Boolean only |
| `&&` | Logical AND | Boolean only |
| `!` | Logical NOT | Boolean only |
| `++` | Increment | Int only |
| `--` | Decrement | Int only |
| `=` | Assignment | any (assignable target) |
| `.` | Member access | data class |
| `..` | Range | Int only |

### Separator

The following characters are the **separators**: left brace (`{`), right brace (`}`), left parenthesis (`(`), right parenthesis (`)`), semicolon (`;`), comma (`,`), colon (`:`), and arrow (`->`).

### Literal

A literal is a source representation of a value of an integer, floating-point, boolean, or string type.

#### Integer literal

Integer literals are always expressed in decimal (base 10). A decimal number is a string of digits (0–9) and is at least one digit long. A leading minus sign is **not** part of an integer literal; negation is handled by the unary `-` operator. To improve readability, an integer literal may contain underscores (`_`) between digits, but not at the beginning or end and not adjacent to another underscore.

The following are valid integer literals: `0`, `100`, `255`, `2500`, `1_000_000`. Integer literals are of type **Int**.

#### Float literal

Float literals represent floating-point numbers. A float literal consists of digits and may include a decimal point and/or an exponent part.

A float literal must have at least one digit. If a decimal point is present, there must be at least one digit either before or after the decimal point (or both). The decimal point may be omitted if an exponent part is present. An optional trailing `f` or `F` suffix may follow the literal.

An exponent part consists of the letter `e` or `E`, optionally followed by a plus sign `+` or minus sign `-`, followed by one or more digits. The exponent part itself is optional when a decimal point is present, but required when there is no decimal point and no `f`/`F` suffix.

The following are valid float literals: `0.0`, `3.14`, `1.23e4`, `5.67E-2`, `1.`, `.5`, `1e4`, `2E-3`, `3.14f`. Float literals are of type **Float**.

#### Boolean literal

There are exactly two boolean literals: `true` and `false`. Boolean literals are of type **Boolean**.

#### String literal

**String literals** consist of zero or more characters enclosed by double quotes (`"`). A string literal can contain any character from the extended ASCII character set (code points 0–255), with the following restrictions:

- **Newline (`\n`) and carriage return (`\r`)** characters cannot appear directly in a string literal. They must be represented using escape sequences (`\n` and `\r`).
- **Backslash (`\`)**, **double quote (`"`)**, and **dollar sign (`$`)** characters must be escaped when they appear in the string content (using `\\`, `\"`, and `\$` respectively).
- **All other characters**, including unprintable ASCII characters (0–31) other than `\n` and `\r`, can appear directly in string literals.

**Escape sequences** are used to represent special characters within a string. All the supported escape sequences are:

    \b   backspace (ASCII 8)
    \f   formfeed (ASCII 12)
    \r   carriage return (ASCII 13)
    \n   newline (ASCII 10)
    \t   horizontal tab (ASCII 9)
    \"   double quote (ASCII 34)
    \\   backslash (ASCII 92)
    \$   dollar sign (ASCII 36)

Only these escape sequences are valid. Hex and unicode escapes such as `\x01` or `\u0041` are **not** supported and will cause an `ILLEGAL_ESCAPE` error.

> **Note on string templates:** Although `$` is reserved (and must be escaped to appear literally), MKotlin Version 1.0 does **not** implement Kotlin string templates. The `$` rule exists to keep the lexical grammar forward-compatible. A `$` that is not part of `\$` inside a string is treated as an ordinary character only when it is escaped; an unescaped `$` immediately followed by a letter or `{` is reserved and produces an `ILLEGAL_ESCAPE` error so that templates can be added later without breaking existing programs. (Implementations targeting Version 1.0 may treat any unescaped `$` as illegal for simplicity; tests will not rely on a bare `$` being valid.)

**String Token Processing:**

- When a valid string literal is recognized, the lexer strips the enclosing double quotes. The token value contains only the string content without the quotes.
- For error cases (`ILLEGAL_ESCAPE` and `UNCLOSE_STRING`), the lexer removes the opening double quote, but the error message includes the problematic content.
- For `UNCLOSE_STRING` errors, the lexeme is the string content after the opening quote **up to but not including** the terminating `\n`, `\r`, or EOF. The newline or carriage return that ends the literal is **not** part of the lexeme.
- For `ILLEGAL_ESCAPE` errors, the error message includes the string content from the beginning (without the opening quote) up to and including the illegal escape sequence.

**Error Detection Order:** The lexer checks for errors in the following order (first match wins):

1. **Illegal escape sequences** are detected first: any backslash followed by a character that is not one of the supported escape characters (`b`, `f`, `r`, `n`, `t`, `"`, `\`, `$`). For example, `\x` in `\x01` triggers `ILLEGAL_ESCAPE` as soon as the unsupported character (`x`) is seen; the lexer does not need to read further digits. A lone `\` at EOF is **not** an illegal escape (there is no following character) and falls through to rule 2.
2. **Unclosed strings** are detected if the string literal is not closed before encountering a newline, carriage return, or end of file (including a trailing `\` with no following character).
3. If neither error occurs, a **valid string literal** is recognized.

A string literal has type **String**.

### Lexical Error Tokens

For lexical errors, the lexer must return the following tokens with specific lexemes:

- **ERROR_TOKEN** with `<unrecognized char>` lexeme: when the lexer detects an unrecognized character.
- **UNCLOSE_STRING** with `<unclosed string>` lexeme: when the lexer detects an unterminated string. The `<unclosed string>` lexeme does not include the opening quote **or** the terminating newline, carriage return, or EOF.
- **ILLEGAL_ESCAPE** with `<wrong string>` lexeme: when the lexer detects an illegal escape in a string. The wrong string runs from the beginning of the string (without the opening quote) to the illegal escape.

---

## Type System

Types limit the values a variable can hold, the values an expression can produce, and the operations supported on those values.

### Primitive Types

#### Int

The keyword `Int` represents an integer type. A value of type `Int` may be positive or negative. Only these operators can act on `Int` values:
`+ - * / % == != < <= > >= ++ -- ..`

#### Float

The keyword `Float` represents a floating-point type. Only these operators can act on `Float` values:
`+ - * / == != < <= > >=`

Note that modulus (`%`), logical operators (`&&`, `||`, `!`), increment/decrement (`++`, `--`), and the range operator (`..`) do **not** apply to `Float` values.

#### Boolean

The keyword `Boolean` represents a logical type with exactly two values, `true` and `false`. Only these operators can act on `Boolean` values:
`&& || ! == !=`

A `Boolean` is **not** interchangeable with `Int`. Conditions in `if`, `while`, and `for` must have type `Boolean`. Arithmetic and relational ordering operators (`<`, `<=`, `>`, `>=`) do not apply to `Boolean`.

#### String

The keyword `String` expresses the string type. The only operators that act on `String` values are assignment (`=`), equality (`==`, `!=`), and use as function arguments / return values. There is no string concatenation in Version 1.0.

#### Unit

The keyword `Unit` is used to express the unit (no meaningful value) type. This type is only used as the return type of a function that has nothing to return. `Unit` is **not** allowed for a variable or parameter declaration.

### Data Class Type

The keywords `data class` introduce a composite data type that groups together members of possibly different types. A data class declaration defines a new type usable throughout the program (subject to declared-before-use).

#### Data Class Declaration

A data class declaration has the following form:

    data class <identifier>(
        <member1>: <type1>,
        <member2>: <type2>,
        ...
        <memberN>: <typeN>
    )

Where:

- `<identifier>` is the data class name.
- Each `<member>` is a member (property) name, and each `<type>` must be an explicit type (`Int`, `Float`, `Boolean`, `String`, or another previously declared data class type).
- A data class can have zero or more members. A data class with zero members is written `data class Empty()`.

**Important Rules:**

- Data class members must have explicit types — they cannot be inferred.
- Nested data class definitions are not supported (you cannot declare a data class inside another).
- Data class members may be of other data class types, provided those types are declared before use.
- Data class names must be unique in the program.
- The data class currently being defined does not count as already declared for typing its own members (a member type cannot be that same incomplete data class).

For example:

    data class Empty()                       // valid: no members

    data class Point(x: Int, y: Int)

    data class Person(name: String, age: Int, height: Float)

#### Data Class Variable Declaration and Construction

A value of a data class type is created by calling its **constructor**, which has the same name as the data class:

    val p1 = Point(10, 20)               // constructor call, p1: Point
    var p2: Point = Point(30, 40)        // explicit type + constructor call

**Construction Rules:**

- The number of arguments must match the number of members.
- Each argument must be in the same order as the declared members, and its type must match the corresponding member's type.
- Each argument can be a literal, a variable, a function call, another constructor call, or any expression evaluating to the correct type.
- A member whose type is another data class is initialized by a constructor call of that type, e.g. `Line(Point(1, 2), Point(3, 4))`, or by a variable of that type.

For example:

    val origin = Point(0, 0)
    val p = Person("John", 25, 1.75)

A data class variable declared with `var` and no initializer (e.g. `var p: Point`) has an undefined value until assigned. (Note that `val` always requires an initializer; see [Variable Declaration](#variable-declaration).)

#### Member Access

Members are accessed using the dot (`.`) operator. The left-hand side may be any expression that evaluates to a data class type:

    val p = Point(10, 20)
    val xCoord = p.x          // read member x
    printInt(p.x)             // use member x in an expression

If a function returns a data class value, its result can be used in member access: `getPoint().x` is valid when `getPoint()` returns a type with member `x`.

**Member assignability:** A member `e.m` is assignable only when the receiver was declared with `var` (or is itself a mutable member chain). A member of a `val`-bound data class value cannot be reassigned. (Implementations may simplify this to: members are assignable iff the root variable is a `var`.)

#### Data Class Operations

- **Assignment**: Data class values can be assigned with `=` to a compatible mutable target. Assignment copies the reference value semantics of the implementation runtime; equality below defines structural comparison.
- **Equality**: Data class types support `==` and `!=`, which compare member-by-member (structural equality), provided both operands have the **same** data class type.
- **Arithmetic / ordering**: Data class types do not support arithmetic or ordering operators.
- **Member access**: The dot (`.`) operator accesses members.

### Variable Declaration

MKotlin supports two kinds of variable bindings:

1. **`val`** — an **immutable** binding. It must be initialized at declaration and cannot be reassigned afterwards.
2. **`var`** — a **mutable** binding. It may be reassigned.

Each kind may use either an inferred type (no annotation) or an explicit type annotation.

#### Variable Declaration Forms

**`val` with inferred type (initializer required):**

    val <identifier> = <expression>

**`val` with explicit type (initializer required):**

    val <identifier>: <type> = <expression>

**`var` with inferred type (initializer required):**

    var <identifier> = <expression>

**`var` with explicit type, initializer optional:**

    var <identifier>: <type> = <expression>
    var <identifier>: <type>

**`var` with inferred type and no initializer** is allowed; the type is then inferred from the first usage (see [Type Inference](#type-inference)):

    var <identifier>

Where `<type>` is one of: `Int`, `Float`, `Boolean`, `String`, or a data class type name.

**Important Rules:**

- A `val` **must** have an initializer and **may not** be reassigned. Reassigning a `val` is a compile-time error.
- A `var` without an initializer and without a type annotation has its type inferred from its **first usage**.
- When using an explicit type with an initializer, the initializer's type must match the declared type.
- If a variable is used in a context where its type cannot be determined, a semantic error occurs.

#### Examples

    // val with inferred type
    val x = 10            // x: Int
    val y = 3.14          // y: Float
    val ok = true         // ok: Boolean
    val msg = "hello"     // msg: String

    // val with explicit type
    val a: Int = 10
    val d: Float = 3.14

    // var, reassignable
    var count = 0         // count: Int
    count = count + 1

    // var with explicit type, no initializer
    var total: Float
    total = 3.14

    // var with no type and no initializer (inferred from first usage)
    var n
    n = 10                // n: Int (from first usage)

---

## Expressions

**Expressions** are constructs made up of operators and operands. In MKotlin there are unary and binary operations.

### Arithmetic Expression

| **Operator** | **Operation** | **Operand Type** | **Result Type** |
| --- | --- | --- | --- |
| `+` | Prefix unary identity | Int or Float | same as operand |
| `-` | Prefix unary negation | Int or Float | same as operand |
| `+` | Infix addition | Int or Float | Int if both Int, else Float |
| `-` | Infix subtraction | Int or Float | Int if both Int, else Float |
| `*` | Infix multiplication | Int or Float | Int if both Int, else Float |
| `/` | Infix division | Int or Float | Int if both Int, else Float |
| `%` | Infix remainder | Int | Int |

If both operands of `+`, `-`, `*`, `/` are `Int`, the result is `Int`; if at least one is `Float`, the result is `Float`. The operands of `%` must both be `Int`.

### Relational Expression

Ordering operators compare `Int` or `Float` operands and produce a **Boolean**:

| **Operator** | **Meaning** | **Operand Type** | **Result Type** |
| --- | --- | --- | --- |
| `<` `<=` `>` `>=` | Ordering | Int or Float | Boolean |

Equality operators produce a **Boolean** and apply when both operands have the same comparable type (`Int`, `Float`, `Boolean`, `String`, or the same data class type):

| **Operator** | **Meaning** | **Operand Type** | **Result Type** |
| --- | --- | --- | --- |
| `==` `!=` | Equality | Int, Float, Boolean, String, or same data class | Boolean |

Mixed `Int`/`Float` equality is allowed and follows numeric promotion (`Int == Float` is valid). `String` equality (`"a" == "b"`, `"a" != "b"`) **is** supported; string ordering (`<`, `<=`, `>`, `>=`) is not.

### Logical Expression

Logical operators `&&` (AND), `||` (OR), `!` (NOT) require **Boolean** operands and produce a **Boolean**.

### Range Expression

The range operator `a..b` requires both operands to be `Int`. A range expression is used **only** as the iterable of a `for` statement (see [For Statement](#for-statement)); it has no first-class value type usable elsewhere in Version 1.0.

### Increment and Decrement Expression

MKotlin supports prefix and postfix increment/decrement, applicable to **Int** only:

| **Operator** | **Operation** | **Operand Type** | **Result Type** |
| --- | --- | --- | --- |
| `++` | Prefix / postfix increment | Int | Int |
| `--` | Prefix / postfix decrement | Int | Int |

The operand must be an assignable `Int` target (a `var` variable or a mutable member).

### Function Call Expression

A **call** is a postfix operation: parentheses with an optional argument list are applied to a **postfix expression**:

    <postfix_expression>(<argument_list>)

where `<argument_list>` is a comma-separated list of expressions (or empty). The callee is not limited to a bare name — any postfix expression may be followed by `()`, consistent with the postfix rules in [Operator Precedence and Associativity](#operator-precedence-and-associativity).

The usual cases are `<identifier>(...)` for a **function call** (return type = the function's return type) or a **constructor call** (return type = that data class type).

### When Expression

`when` may be used as an expression that produces a value (see [When Statement](#when-statement) for the statement form and full semantics). As an expression, every branch must produce a value of the same type, and an `else` branch is required:

    val sign = when {
        n > 0 -> 1
        n < 0 -> -1
        else -> 0
    }

Each branch has the form `<labels> -> <expression>`. Branch bodies must be expressions, not blocks. Optional separators (newlines or `;`) may appear between branches:

    val x = when (d) { 1 -> 10; else -> 0 }   // valid

### Expression Layout

An `<expression>` must be written on a **single logical line**: it must not contain a `NEWLINE` between its operators and operands. For example, `val x = 1 +` followed by a newline and `2` is a **syntax error** — the newline ends the variable-declaration statement before the expression is complete. Long expressions must stay on one line, or use parentheses on that same line: `val x = (1 + 2)`.

### Assignment Expression

An **assignment expression** assigns a value to an assignable target and may be used as an expression:

    <assignable> = <expression>

where `<assignable>` is a `var` variable or a mutable member access. Assignment is right-associative, allowing chained assignments such as `x = y = z = 10`, parsed as `x = (y = (z = 10))`. The type of an assignment expression is the type of its target. Assigning to a `val` is a compile-time error.

### Operator Precedence and Associativity

From highest to lowest:

| **Operator** | **Associativity** |
| --- | --- |
| `.` (member access) | left |
| `++`, `--` (postfix), `()` (call) | left |
| `++`, `--` (prefix), `!`, unary `-`, unary `+` | right |
| `*`, `/`, `%` | left |
| `+`, `-` (binary) | left |
| `..` (range) | left |
| `<`, `<=`, `>`, `>=` | left |
| `==`, `!=` | left |
| `&&` | left |
| `||` | left |
| `=` | right |

**Postfix grouping examples** (member access `.` is a postfix operator; higher precedence means it binds to its operands more tightly, not that it is evaluated first in time):

| **Source** | **Parsed as** |
| --- | --- |
| `getPoint().x` | `(getPoint()).x` |
| `(a++).x` | postfix `++` on `a`, then member `.x` on the result |
| `(x.a)++` | member access `x.a`, then postfix `++` on that |

### Evaluation Order

The left-hand operand of a binary operator is evaluated before any part of the right-hand operand. In a function or constructor invocation, the actual arguments are evaluated left to right. The logical operators `&&` and `||` use **short-circuit** evaluation: evaluation stops as soon as the result is known.

---

## Statements

A statement indicates the action a program performs. Statements are separated by newlines (or optional semicolons). The kinds of statements are described below.

### Separators and Statement/Declaration Lists

A **separator** (`sep`) is either a `NEWLINE` token or a semicolon (`;`). Separators are used to delimit declarations and statements in lists.

| **Context** | **Grammar pattern** | **Meaning** |
| --- | --- | --- |
| Top-level declaration list | `decl (sep+ decl)* sep*` | At least one `sep` between consecutive declarations; optional `sep` after the last |
| Statement list (function body, block) | `stmt (sep+ stmt)* sep*` | At least one `sep` between consecutive statements; optional `sep` after the last |
| `when` branch list | each branch ends with optional `sep*` | Separators between branches are optional; `;` is allowed |
| Body of `if` / `while` / `for` / `else` | single `<statement>` | **No** `sep` required after the body — the construct ends at the natural end of that statement |

`sep+` means **one or more** separators — multiple semicolons (`;;`) or multiple newlines between items are valid. `sep*` means zero or more — trailing separators after the last item are optional.

Examples:

    fun main() {} ;; fun cal() {}     // valid: sep+ between declarations

    fun main() {
        val x = 10 ;; continue        // valid: sep+ between statements
    }

    fun main() { {} break }           // invalid: missing sep between {} and break

    fun main() { continue }           // valid: single statement, no sep needed before }

    while (i < 10) { i++ }
    printInt(0)                       // valid: newline between while stmt and next stmt in block

**Statement list:** A `<statement_list>` is a (possibly empty) sequence of statements. This applies in a **function body** and in a **block** (`{ ... }`). An empty statement list (e.g. `{ }`) is valid.

Each branch of a `when` statement or `when` expression is a **single** `<statement>` or `<expression>`, not a statement list. To run multiple statements in one branch, use a **block** as that branch's body (e.g. `1 -> { printInt(1); printInt(2) }`).

### Variable Declaration Statement

A variable declaration declares a `val` or `var` binding as described in [Variable Declaration](#variable-declaration):

    val <identifier> = <expression>
    val <identifier>: <type> = <expression>
    var <identifier> = <expression>
    var <identifier>: <type> = <expression>
    var <identifier>: <type>
    var <identifier>

### Block Statement

A block begins with `{` and ends with `}` and contains a (possibly empty) statement list:

    {
        val x = 10
        val y = 20
        printInt(x + y)
    }

### If Statement

The **if statement** conditionally executes one of two statements:

    if (<expression>) <statement>
    if (<expression>) <statement> else <statement>

where `<expression>` must have type **Boolean**. If it is `true`, the first `<statement>` runs; otherwise, if an `else` is present, the `else` statement runs.

When nested if statements are used, an `else` associates with the nearest `if` lacking an `else`. In `if (a) if (b) s1 else s2`, the `else` binds to `if (b)`.

> MKotlin also allows `if`/`else` to be used as an **expression** (Kotlin-style), where both branches must produce a value of the same type and an `else` is required: `val m = if (a > b) a else b`.

**If expression** (used where a value is needed — right-hand side of `=`, function argument, `return`, nested in another expression):

    if (<expression>) <expression> else <expression>

Branch bodies must be `<expression>` tokens, **not** blocks. Block braces `{ }` are statements and cannot appear as the direct branch of an if expression:

    val x = if (a) 1 else 0           // valid
    val x = if (a) { 1 } else { 2 } // invalid syntax

No separator is required after the body of an `if` statement or its `else` branch — each is a single `<statement>`.

For example:

    if (flag) {
        printInt(1)
    } else {
        printInt(0)
    }

### While Statement

The **while statement** repeats while a condition is true:

    while (<expression>) <statement>

The `<expression>` must have type **Boolean**. No separator is required after the loop body — it is a single `<statement>`.

For example:

    var i = 0
    while (i < 10) {
        printInt(i)
        i++
    }

### For Statement

The **for statement** iterates a loop variable over an integer range:

    for (<identifier> in <start>..<end>) <statement>

Where:

- `<identifier>` introduces a fresh, immutable loop variable of type `Int`, visible only inside the loop body. It cannot be reassigned inside the body.
- `<start>` and `<end>` are `Int` expressions. Iteration covers `<start>, <start>+1, ..., <end>` inclusive (an empty iteration if `<start> > <end>`).

Lexical scope for the loop variable and body follows [Scope Rules](#scope-rules). No separator is required after the loop body — it is a single `<statement>`.

For example:

    for (i in 0..9) {
        printInt(i)
    }

### When Statement

The **when statement** selects among multiple branches. MKotlin's `when` does **not** fall through: exactly one matching branch executes, then control leaves the `when`.

There are two forms.

**Subject form** — matches a subject value against branch values:

    when (<expression>) {
        <value_1> -> <statement>
        <value_2>, <value_3> -> <statement>
        ...
        else -> <statement>
    }

Where:

- `<expression>` (the subject) must have a comparable type (`Int`, `Float`, `Boolean`, or `String`).
- Each branch label is one or more comma-separated expressions whose type must match the subject's type. A branch matches when the subject equals one of its labels.
- The `else` branch is optional in statement position and matches when no other branch matches.

**Conditionless form** — each branch is a Boolean guard:

    when {
        <boolean_expr_1> -> <statement>
        <boolean_expr_2> -> <statement>
        ...
        else -> <statement>
    }

Each guard must have type **Boolean**; the first `true` guard's statement executes.

For both forms, the right-hand side of `->` is a single statement (commonly a block). At most one `else` branch is allowed. Optional separators (newlines or `;`) may appear after each branch; they are not required. The branch list may be **empty** — a `when` with no branches (and no `else`) is valid syntax and has no effect:

    when (a) { }              // valid: empty when statement

    when (d) { 1 -> 10; else -> 0 }   // valid: semicolon between branches

This differs from **when expression** (see [When Expression](#when-expression)), where every branch must produce a value of the same type and an `else` branch is required.

For example:

    when (day) {
        1 -> printInt(1)
        2, 3 -> printInt(2)
        else -> printInt(0)
    }

    when {
        n > 0 -> printString("positive")
        n < 0 -> printString("negative")
        else -> printString("zero")
    }

### Break Statement

`break` leaves the innermost enclosing loop (`while` or `for`). It must reside within a loop; otherwise a semantic error (`MustInLoop`) is generated. Note that, unlike C, `break` is **not** used inside `when` (there is no fall-through).

    break

### Continue Statement

`continue` skips the rest of the current loop iteration and proceeds to the next. It must reside within a loop; otherwise a semantic error (`MustInLoop`) is generated.

    continue

### Return Statement

A **return statement** transfers control to the caller:

    return <expression>

or for `Unit` functions:

    return

The type of the returned expression must match the function's return type.

### Expression Statement

An **expression statement** is an expression used for its side effects (function calls, assignments, increments/decrements):

    printInt(x)      // function call
    x = 5            // assignment
    x = x + 1        // assignment
    x++              // increment

---

## Type Inference

### Complete Type Inference System

MKotlin uses complete type inference where types are inferred throughout the program from multiple sources, as described below. Inference is **local** and **deterministic**: it does not perform whole-program constraint solving.

### Type Inference Rules

#### Rule 1: Literal Type Inference

- **Integer literals** (`123`, `0`, `1_000`) → `Int`
- **Float literals** (`9.0`, `12e8`, `1.`, `.5`, `3.14f`) → `Float`
- **Boolean literals** (`true`, `false`) → `Boolean`
- **String literals** (`"hello"`) → `String`

#### Rule 2: Variable Declaration Type Inference

**2.1 `val`/`var` with initializer:** The type is the type of the initializer expression.

    val x = 10          // Int
    val y = 3.14        // Float
    val ok = 1 < 2      // Boolean
    val msg = "hello"   // String
    val z = x + y       // Float (Int + Float)

**2.2 `var` without initializer and without annotation:** The type is inferred from the **first usage**, by the inference context of that usage (see 2.2.1):

- If first usage is an **assignment** `v = rhs`: the type is the type of `rhs` (which must itself be checkable, including the integer-literal anchor below).
- If first usage is as a **function/constructor argument**: the parameter (or member) type is the expected type of the **whole** argument expression and may fix a lone `var` identifier argument.
- If first usage is a **return** value: the function's return type is the expected type of the **whole** returned expression.
- If no rule fixes the `var`, a `TypeCannotBeInferred` semantic error occurs.

**2.2.1 Inference contexts (what fixes an un-annotated `var`, what does not):**

MKotlin uses **local** inference, not "propagate any outer type into every sub-expression":

- **Assignment:** `lhs = rhs` — if `lhs` already has a definite type, `rhs` is checked against it. This can fix one unknown `var` on the RHS when the rest of the expression supplies enough information.
- **Explicitly typed initializer / declaration:** `val v: T = expr` (or a `var v: T`) — `T` applies to **checking** the full expression; it does **not** independently assign types to unrelated un-annotated `var`s appearing only as operands inside `expr`.
- **Function/constructor call:** Parameter (member) types apply as the expected type of each **argument expression as a whole**; they fix a `var` **identifier** that is the entire argument (e.g. `printInt(x)`), but do not recursively infer every leaf of a compound argument.
- **Integer-literal anchor:** For arithmetic `+`, `-`, `*`, `/`, if one operand is an undetermined `var` and the other is an **integer literal**, the unknown operand is taken as `Int`. This is a deterministic tie-break, not the only valid typing.

    var a
    a = 10              // a: Int (assignment)
    var b
    b = 3.14            // b: Float
    var c
    c = a + b           // c: Float
    var d
    d = readInt()       // d: Int (function return type)

**2.3 Explicit type with initializer:** The variable's type is the declared type; the initializer's type must match it.

    val x: Int = 10
    val y: Float = 3.14
    val s: String = "hello"

**2.4 Explicit type without initializer (`var` only):** The variable's type is the declared type; it has an undefined value until assigned.

    var a: Int
    var b: Float
    a = 10
    b = 3.14

#### Rule 3: Expression Type Inference

**3.1 Primary expressions:**

- **Identifier** → declared type (a variable's type, or for a bare function name used in a call, the function's return type).
- **Literal** → Rule 1.
- **Parenthesized** `(expr)` → type of `expr`.
- **Member access** `expr.m` → type of member `m`; `expr` must be a data class type and `m` one of its members.
- **Constructor call** `C(args)` → the data class type `C`.

**3.2 Unary expressions:**

| **Expression** | **Operand Type** | **Result Type** |
| --- | --- | --- |
| `+expr`, `-expr` | Int or Float | same as operand |
| `!expr` | Boolean | Boolean |
| `++expr`, `--expr` | Int | Int |

**3.3 Postfix expressions:**

| **Expression** | **Operand Type** | **Result Type** |
| --- | --- | --- |
| `expr++`, `expr--` | Int | Int |
| `expr(args)` | function call | function's return type |

**3.4 Binary expressions:**

Arithmetic (`+ - * /`): `Int op Int → Int`; if either operand is `Float`, result is `Float`. `%`: `Int op Int → Int`.

Ordering (`< <= > >=`): `Int`/`Float` operands → `Boolean`.

Equality (`== !=`): same comparable type (`Int`, `Float`, `Boolean`, `String`, or the same data class; with `Int`/`Float` promotion) → `Boolean`.

Logical (`&& ||`): `Boolean` operands → `Boolean`. `!`: `Boolean` → `Boolean`.

**3.5 Function call** `f(args)` → return type of `f`. The return type may be declared or inferred from the function's return statements.

**3.6 Assignment** `target = expr` → type of `target`; the type of `expr` must match.

#### Rule 4: Type Compatibility and Checking

**4.1 Assignment compatibility:** The target type must match the value type. For explicit declarations, the initializer's type must match the declared type. `Int` may be assigned where `Float` is expected (numeric widening); the reverse is **not** allowed.

**4.2 Operator compatibility:** Each operator applies only to its specified operand types.

**4.3 Call compatibility:** Argument types must match parameter types (with `Int → Float` widening permitted), and the argument count must match the parameter count. The same applies to constructor calls versus data class members.

#### Rule 5: Function Return Type

- Return types may be declared (`: T`) or omitted (inferred).
- When omitted, the return type is inferred from the **first** value-returning `return` statement. If there is none (only bare `return` or no return), the inferred type is `Unit`.
- All `return` statements must agree with the inferred/declared type (or be value-less for `Unit`); a mismatch is a `TypeMismatchInStatement` error.
- The inferred return type is a property of the whole body; static checking may use multiple internal passes.

### Strict Operator Typing

- **Arithmetic** (`+ - * /`): `Int` or `Float` (result `Int` if both `Int`, else `Float`).
- **Modulus** (`%`): `Int` only.
- **Ordering** (`< <= > >=`): `Int` or `Float`, result `Boolean`.
- **Equality** (`== !=`): same comparable type (`Int`, `Float`, `Boolean`, `String`, or the same data class), result `Boolean`.
- **Logical** (`&& || !`): `Boolean` only, result `Boolean`.
- **Increment/decrement** (`++ --`): `Int` only.
- **Range** (`..`): `Int` only.

**Restrictions:**

- `"hello" + "world"` is a type error (no string concatenation).
- `"a" < "b"` is a type error (no string ordering). `"a" == "b"` is valid.
- `3.14 % 2` is a type error (modulus is `Int` only).
- `true && 1` is a type error (`&&` requires `Boolean` operands; `Int` is not `Boolean`).
- `if (1) ...` is a type error (condition must be `Boolean`).
- `++x` where `x` is `Float` is a type error.

---

## Scope Rules

Names are resolved under **lexical (static) scope**: visibility depends only on the nesting of declarations in the source text, not on run-time order.

There are two broad levels: **global** (functions, data classes) and **local** (parameters, variables, loop variables inside functions).

### Global Scope

All function names and data class names have global scope. A use of a function, a constructor, or a data class as a type must still obey **declared-before-use** in the source text; global scope does not permit forward references.

### Local Scope

Parameters, variables, and `for` loop variables are **local**. Each declaration is visible from the declaration through the end of the innermost scope that contains it. Resolution searches from the innermost scope outward. The initializer of a variable declaration is **not** in the scope of that variable; the name is in scope only after the entire declaration.

**Blocks:** A block `{ ... }` introduces a new inner scope. An inner scope may **shadow** a local from an outer scope by redeclaring the same identifier. Reusing a **parameter** name in the function's top-level body scope is a `Redeclared` error (see the semantic reference).

**`for` statements:** In `for (i in a..b) <body>`:

- The loop variable `i` is introduced in an inner scope nested under the enclosing scope and is visible **only** within the loop construct (header and body). It does **not** remain in scope after the `for`.
- The loop `<body>` is elaborated in an inner scope nested under the loop-variable scope, so a declaration in `<body>` may shadow `i`.

---

## Input and Output

MKotlin provides the following built-in functions:

| **Function Prototype** | **Semantic** |
| --- | --- |
| `fun readInt(): Int` | Read an integer from the keyboard |
| `fun readFloat(): Float` | Read a floating-point number from the keyboard |
| `fun readBool(): Boolean` | Read a boolean (`true`/`false`) from the keyboard |
| `fun readString(): String` | Read a string from the keyboard |
| `fun printInt(value: Int): Unit` | Write an integer to the screen |
| `fun printFloat(value: Float): Unit` | Write a floating-point number to the screen |
| `fun printBool(value: Boolean): Unit` | Write a boolean to the screen |
| `fun printString(value: String): Unit` | Write a string to the screen |

---

## Example Programs

### Example 1: Hello World

    fun main() {
        printString("Hello, World!")
    }

### Example 2: Simple Calculator

    fun add(x: Int, y: Int): Int {
        return x + y
    }

    fun multiply(x: Int, y: Int): Int {
        return x * y
    }

    fun main() {
        val a = readInt()
        val b = readInt()

        val sum = add(a, b)
        val product = multiply(a, b)

        printInt(sum)
        printInt(product)
    }

### Example 3: Loops with Conditions

    fun main() {
        val n = readInt()

        var i = 0
        while (i < n) {
            printInt(i)
            i++
        }

        for (j in 0..n) {
            if (j % 2 == 0) {
                printInt(j)
            }
        }
    }

### Example 4: Factorial Function

    fun factorial(n: Int): Int {
        if (n <= 1) {
            return 1
        } else {
            return n * factorial(n - 1)
        }
    }

    fun main() {
        val num = readInt()
        val result = factorial(num)
        printInt(result)
    }

### Example 5: when as Statement and Expression

    fun classify(n: Int): String {
        return when {
            n > 0 -> "positive"
            n < 0 -> "negative"
            else -> "zero"
        }
    }

    fun main() {
        val n = readInt()
        printString(classify(n))

        when (n % 3) {
            0 -> printString("divisible by 3")
            1, 2 -> printString("not divisible by 3")
            else -> printString("unreachable")
        }
    }

### Example 6: Data Class Usage

    data class Point(x: Int, y: Int)

    data class Person(name: String, age: Int, height: Float)

    fun main() {
        // Construction
        var p1 = Point(10, 20)
        val p2 = Point(30, 40)

        // Member access
        printInt(p2.x)
        printInt(p2.y)

        // Structural equality
        val same = Point(10, 20) == p1     // true
        printBool(same)

        // Reassign a var-bound member
        p1.x = 99
        printInt(p1.x)

        val person = Person("John", 25, 1.75)
        printString(person.name)
        printInt(person.age)
        printFloat(person.height)
    }

---

For AST node conventions and `repr()` formats used in Assignment 2, see [AST Representation](mkotlin-ast_representation.md).

## Grammar Summary

An MKotlin program is a (possibly empty) sequence of data class declarations and function declarations. Consecutive declarations are separated by at least one newline or semicolon.

**Data Class Declarations:**

- Each defines a new composite type with named members of explicit types.
- Members cannot be inferred; nested data class definitions are not supported.
- Members may be other (previously declared) data class types.

**Function Declarations:**

- Each has the `fun` keyword, an identifier, a parameter list, an optional return-type annotation, and a body block.
- Function names must be unique (no overloading).

The main structural elements include:

- **Data classes**: composite types with named members of explicit types.
- **Functions**: declarations with parameters, an optional return type, and a body.
- **Statements**: variable declarations, control flow (`if`, `while`, `for`, `when`), `break`, `continue`, `return`, expression statements (including assignments), and blocks.
- **Expressions**: primary expressions (identifiers, literals, parenthesized, member access, constructor and function calls), unary and binary operations following operator precedence, range expressions, and postfix operations.
- **Types**: `Int`, `Float`, `Boolean`, `String`, `Unit`, data class types, and inference via `val`/`var`.
- **Literals**: integer, float, boolean, and string literals.

**Operator Precedence** (highest to lowest):

1. Member access (`.`)
2. Postfix (`++`, `--`), call (`()`)
3. Prefix/unary (`!`, unary `-`, unary `+`, `++`, `--`)
4. Multiplicative (`*`, `/`, `%`)
5. Additive (`+`, `-`)
6. Range (`..`)
7. Ordering (`<`, `<=`, `>`, `>=`)
8. Equality (`==`, `!=`)
9. Logical AND (`&&`)
10. Logical OR (`||`)
11. Assignment (`=`)

**Lexical and layout rules** (summary):

- Token `RANGE` (`..`) takes precedence over float literals such as `1.` when lexing `1..2`.
- Expressions do not contain newlines; statement/declaration lists use `sep+` between items and optional `sep*` after the last.
- Unclosed block comments at EOF are not a defined lexical error.
- `UNCLOSE_STRING` lexemes exclude the opening quote and any terminating `\n`/`\r`.

**Note:** The complete grammar rules must be defined in the ANTLR4 grammar file (`MKotlin.g4`) by the student. This specification provides the requirements and examples; the detailed grammar implementation is part of the assignment.

---

## Revision History

### Version 1.2 (August 2026)

Documentation consistency fix for `String` equality. The Type System already listed `==` / `!=` on `String`; the Equality Expression section and Operator table incorrectly said otherwise. They now agree: `String` equality is supported; string ordering and concatenation remain unsupported.

### Version 1.1 (July 2026)

Documentation clarifications for Assignment 1 (lexer/parser). **No change to the MKotlin language semantics** — only the specification text was expanded to match the reference grammar and common student questions.

- **Newlines and Layout** — when a newline may appear before `{` or inside `()` (function/`when` headers vs `if`/`while`/`for` bodies).
- **Lexical Tokenization** — `RANGE` (`..`) vs float literals (`1.`, `.5`); empty parentheses may not contain `NEWLINE`.
- **Separators and Statement/Declaration Lists** — `sep+` / `sep*` rules for declarations, statements, and `when` branches; multiple `;;` allowed.
- **String errors** — `UNCLOSE_STRING` lexeme excludes terminating `\n`/`\r`; `\` at EOF is unclosed string, not `ILLEGAL_ESCAPE`.
- **Comments** — line-comment end-of-line includes `\r`; unclosed block comment at EOF is not a defined lexical error.
- **Expressions** — single-line expressions; if/when expression branch rules; postfix call on any postfix expression; postfix grouping examples (`getPoint().x`, `(a++).x`).
- **When statement** — empty branch list allowed; optional separators between branches.
- **Control flow** — no separator required after a single-statement `if`/`while`/`for`/`else` body.

### Version 1.0 (June 2026)

Initial public specification.

---

**End of Specification**
