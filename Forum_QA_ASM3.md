_---
title: Forum Q&A - MKotlin Static Checker
tags: [mkotlin, static-checker, compiler, forum-qa, btl]
source: Forum_QA.txt
---

# Forum Q&A — MKotlin Static Checker

> [!info] Về tài liệu này
> Tổng hợp các câu hỏi–trả lời trên diễn đàn môn học liên quan đến đặc tả ngữ nghĩa (semantic constraints) và các lỗi của Static Checker trong MKotlin.

## Mục lục

1. [[#1. `val` không có initializer — lỗi ở đâu?]]
2. [[#2. Phân biệt UndeclaredFunction vs UndeclaredClass khi `X(args)` không phân giải được]]
3. [[#3. Redeclared Variable hay Redeclared Constant khi `val x` trùng tên parameter?]]
4. [[#4. Mâu thuẫn giữa Local Scope và quy tắc Redeclared trong vòng `for`]]
5. [[#5. `for (i in 0..3) var i = 4` (không có ngoặc) có bị Redeclared không?]]
6. [[#6. So sánh bằng cho `String` — hai đoạn spec mâu thuẫn nhau]]
7. [[#7. Node lỗi cho `++` / `--` khi nằm trong biểu thức lồng hoặc sai cả hai điều kiện]]
8. [[#8. `when {... -> 1; else -> 1.0}` có hợp lệ không?]]
9. [[#9. Int → Float widening có áp dụng cho `return` không?]]
10. [[#10. `when (1.0) {1 -> ...}` và `when (1) {1.0 -> ...}` có hợp lệ không?]]
11. [[#11. Rule 5 về suy luận kiểu trả về — đệ quy và `return` trống lẫn có giá trị]]
12. [[#12. Node lỗi TypeCannotBeInferred cho UnaryOp, CallExpr, MemberAccess]]
13. [[#13. `var a; if (a) {}` — node lỗi là `Id(a)` hay `If(...)`?]]
14. [[#14. Anchor kiểu cho `var a; var b = 1; b = a;` và `var b = a + 1.0`]]
15. [[#15. `var a; var b; a = b;` — hai unknown lẫn nhau thì bắt lỗi thế nào?]]
16. [[#16. `When` statement khi subject không phải kiểu so sánh được]]
17. [[#17. `val p = Vec(1, 2)` khi `Vec` chưa khai báo — UndeclaredFunction hay UndeclaredClass?]]
18. [[#18. Đệ quy không neo được kiểu trả về: `fun f() { return f() }`]]
19. [[#19. `var x` không annotation, không initializer, không dùng — và hợp nhất kiểu nhánh `when` expression]]

---

## 1. `val` không có initializer — lỗi ở đâu?

**Q:**
Trong file `mkotlin-semantic_constraints_and_errors.md` có ghi ở phần Variable Declaration:

> "A val requires an initializer; a val without one is a structural error surfaced as `TypeCannotBeInferred` on the declaration (there is nothing to infer from and reassignment is forbidden)."

Theo hiểu là khai báo `val` không có initializer sẽ raise `TypeCannotBeInferred`. Nhưng trong file `mkotlin_specification.md` có liệt kê các cấu trúc hợp lệ cho khai báo `val` là:

```kotlin
val <identifier> = <expression>
val <identifier>: <type> = <expression>
```

Không biết nếu đầu vào là khai báo `val` không có initializer thì phần **parser** hay phần **checker** sẽ báo lỗi?

**A:**
Đọc lại kỹ các phần sau trong `mkotlin-semantic_constraints_and_errors.md`:

- **General Principles** / đoạn mở đầu — checker làm việc trên AST và báo các lỗi ngữ nghĩa.
- **Error Types** — `TypeCannotBeInferred` là một trong các lỗi của StaticChecker.
- **Variable Declaration** — đúng đoạn đã trích: `val` không có initializer được surface bằng `TypeCannotBeInferred` trên declaration.

> Câu trả lời đã nằm trong các đoạn đó.

---

## 2. Phân biệt UndeclaredFunction vs UndeclaredClass khi `X(args)` không phân giải được

**Q:**
`X(args)` mà `X` không phân giải được thành gì cả thì làm sao biết nên báo `UndeclaredFunction` hay `UndeclaredClass`?

- **UndeclaredFunction** — A call `f(args)` where `f` is not a declared (or built-in) function name. (A constructor call to an undeclared data class name is `UndeclaredIdentifier` if `f` is also not a type, but if the name is being used specifically in type position, see `UndeclaredClass`.)
- **UndeclaredClass** — Use of a data class type name (in an annotation, parameter type, member type, or constructor call) that has not been declared.

Hai test mẫu:

```python
def test_004_undeclared_function():
    """4. UndeclaredFunction"""
    src = "fun main() {\n val a = compute(1)\n}"
    assert Checker.check(src) == "Undeclared Function: compute"

def test_005_undeclared_class():
    """5. UndeclaredClass"""
    src = "fun main() {\n val p = Vec(1, 2)\n}"
    assert Checker.check(src) == "Undeclared Class: Vec"
```

Cả hai đều không có cơ sở ngữ cảnh đầy đủ nào để phân biệt hết. Nếu dựa theo luật báo lỗi thì có vẻ nên báo `UndeclaredIdentifier` chứ?

**A:**
Quan sát đúng ở chỗ: với `X(args)` mà `X` không phân giải được thành hàm, data class hay biến nào, thì bản thân lời gọi không cung cấp thêm ngữ cảnh nào để phân biệt gọi hàm với gọi constructor. Nhưng kết luận `UndeclaredIdentifier` thì không đúng.

Quy tắc áp dụng như sau:

- **Vị trí lời gọi** — `X(args)` với `X` chưa được khai báo: báo `UndeclaredFunction(X)`. Vị trí lời gọi được coi là gọi hàm theo mặc định; nó chỉ được coi là gọi constructor khi `X` là tên một data class đã khai báo.
- **Vị trí kiểu** — tên xuất hiện ở annotation của biến, kiểu tham số, kiểu member, hoặc kiểu trả về: báo `UndeclaredClass(X)`. Đây là nơi duy nhất mà tên chắc chắn đang được dùng như một kiểu.
- **Identifier trần** — tên dùng như một giá trị, không có `()` theo sau và không nằm trong scope: báo `UndeclaredIdentifier(X)`.

Vì lỗi đầu tiên theo thứ tự duyệt được báo, nên khi một khai báo có cả annotation và lời gọi, annotation được kiểm tra trước:

```kotlin
val p: Vec = Vec(1, 2)  // UndeclaredClass: Vec  (từ annotation)
val a = compute(1)      // UndeclaredFunction: compute
printInt(y)             // UndeclaredIdentifier: y
```

Quy ước viết hoa chữ cái đầu **không phải** là căn cứ phân loại — MKotlin không gán ý nghĩa nào cho hoa/thường trong tên (xem mục Identifier của Specification).

> Phần mô tả của hai loại lỗi này sẽ được làm rõ lại theo đúng quy tắc trên.

---

## 3. Redeclared Variable hay Redeclared Constant khi `val x` trùng tên parameter?

**Q:**
Trong trường hợp parameter `x` bị khai báo lại bằng `val x`, lỗi đúng là `Redeclared Variable` hay `Redeclared Constant`? Vì spec có chỗ ghi `val` là Constant, nhưng ở `test006()` mẫu thì lại báo lỗi là `Redeclared Variable`.

**A:**
Dùng kind `Variable` cho mọi khai báo biến bị trùng tên, không phân biệt `val` hay `var`:

```kotlin
fun f(x: Int) {
    val x = 5    // Redeclared Variable: x
}

fun g() {
    var a = 1
    val a = 2    // Redeclared Variable: a
}
```

Kind `Constant` có mặt trong `static_error.py` nhưng **không** được dùng để báo lỗi Redeclared — thông báo cho khai báo biến luôn là `Redeclared Variable: <tên>`.

Các kind còn lại giữ đúng vai trò của chúng: `Parameter` cho tên tham số trùng nhau trong cùng danh sách tham số, `Function` cho tên hàm, `Class` cho tên data class, và `Member` cho tên member trong một data class.

> Phần mô tả của lỗi này sẽ được viết lại để bỏ phần cho phép chọn giữa hai kind.

---

## 4. Mâu thuẫn giữa Local Scope và quy tắc Redeclared trong vòng `for`

**Q:**
Specification mục Local Scope viết thân vòng lặp là scope con lồng dưới scope của biến lặp, "so a declaration in `<body>` may shadow `i`", nên `for (i in 1..3) { val i = 5 }` là hợp lệ. Semantic Constraints mục For có câu "Redeclaring it as a top-level body declaration in the same loop-variable scope → Redeclared" — mệnh đề "in the same loop-variable scope" là điều kiện mà theo mô hình scope của spec thì khai báo trong thân không bao giờ thoả, nên 2 câu đó mâu thuẫn nhau. Hiểu vậy có đúng không?

**A:**
Hiểu đúng. Thân vòng lặp được kiểm tra trong một scope con của scope chứa biến lặp. Vì vậy:

```kotlin
for (i in 1..3) {
    val i = 5
}
```

là hợp lệ; biến `i` được khai báo trong thân vòng lặp che khuất biến lặp `i`.

`Redeclared` chỉ xảy ra khi hai khai báo cùng tên thuộc cùng một scope. Câu "top-level body declaration in the same loop-variable scope" trong Semantic Constraints chưa phù hợp với mô hình scope trên và sẽ được điều chỉnh để tránh gây nhầm lẫn.

---

## 5. `for (i in 0..3) var i = 4` (không có ngoặc) có bị Redeclared không?

**Q:**
Với trường hợp này thì có bị lỗi Redeclare không: `for (i in 0..3) var i = 4` (không có ngoặc)?

**A:**
Đọc lại kỹ các phần sau:

- `mkotlin_specification.md` — mục For Statement (`for (...) <statement>`) và mục Local Scope (đoạn về for: thân vòng lặp được elaborate trong scope con của scope biến lặp, nên khai báo trong thân được phép che khuất biến lặp).
- `mkotlin-semantic_constraints_and_errors.md` — mục For (thân được kiểm trong scope lồng dưới scope biến lặp; khai báo trong thân che khuất biến lặp không phải Redeclared).

> Câu trả lời đã nằm trong các đoạn đó.

---

## 6. So sánh bằng cho `String` — hai đoạn spec mâu thuẫn nhau

**Q:**
Trong spec của `mkotlin_specification.md` có 2 mô tả mâu thuẫn nhau:

> "so sánh bằng cho `String` **không** được hỗ trợ trong Phiên bản 1.0." — ở phần Biểu thức số học.

và

> "Các toán tử duy nhất tác động lên giá trị `String` là phép gán (`=`), so sánh bằng (`==`, `!=`), và dùng làm đối số hàm / giá trị trả về. Không có phép nối chuỗi trong Phiên bản 1.0." — ở phần hệ thống kiểu dữ liệu.

Vậy có được so sánh bằng cho 2 `String` hay không?

**A:**
Quan sát đúng — hai đoạn trong Specification đang mâu thuẫn nhau. Quy tắc áp dụng là: **được** so sánh bằng hai giá trị `String`.

```kotlin
val ok = "a" == "b"    // hợp lệ, kiểu Boolean
val diff = "a" != "b"  // hợp lệ
```

Điều này khớp với mục Type System → String (liệt kê `==`/`!=` cho String) và với When Statement (subject có thể là String). Phần Equality Expression ghi "String equality is not supported" sẽ được chỉnh lại cho thống nhất.

> **Lưu ý:** so sánh thứ tự trên String (`<`, `<=`, `>`, `>=`) và nối chuỗi bằng `+` vẫn không được hỗ trợ.

---

## 7. Node lỗi cho `++` / `--` khi nằm trong biểu thức lồng hoặc sai cả hai điều kiện

**Q:**
Có 2 chỗ về `++` / `--` chưa rõ:

**a)** Node truyền vào `TypeMismatchInStatement` khi chỗ sai nằm trong biểu thức lồng.

```kotlin
fun main() {
    val i = 0
    val x = i++ + 1
}
```

Vậy node truyền vào exception ở đây là `PostfixOp(++, Id(i))`, hay là cả `VarDecl(...)`?

**b)** Khi cả hai điều kiện của `++` cùng sai.

Tài liệu ghi: "operand must be an assignable Int target -> else `TypeMismatchInExpression` (wrong type) or `TypeMismatchInStatement` (assigning a val/loop variable), per the offending condition." Nhưng cả hai điều kiện có thể sai cùng lúc trên cùng một node:

```kotlin
fun main() {
    val f = 1.0
    f++
}
```

`f` vừa sai kiểu (Float chứ không phải Int), vừa không gán được (là val). Vậy trường hợp này là `TypeMismatchInExpression` hay `TypeMismatchInStatement`?

**A:**

**1. Node khi `++` nằm trong biểu thức lồng**

```kotlin
fun main() {
    val i = 0
    val x = i++ + 1
}
```

Lỗi là `TypeMismatchInStatement` với node:

```
PostfixOp(++, Id(i))
```

Không dùng `VarDecl(...)`. Node là đúng phép `++`/`--` vi phạm (tương tự prefix thì là `UnaryOp`), kể cả khi nó nằm trong initializer hay biểu thức lớn hơn.

**2. Khi vừa sai kiểu vừa không gán được**

```kotlin
fun main() {
    val f = 1.0
    f++
}
```

Báo `TypeMismatchInExpression` với node `PostfixOp(++, Id(f))`.

Thứ tự kiểm cho `++`/`--`:

1. Operand phải có kiểu Int — sai → `TypeMismatchInExpression`.
2. Operand phải gán được (var / member mutable) — sai → `TypeMismatchInStatement`.

Ở đây `f` là Float nên điều kiện (1) thất bại trước; không xét tiếp điều kiện (2).

> **Tham chiếu:** nếu chỉ sai gán được (`val i = 0; i++`) thì mới là `TypeMismatchInStatement`; nếu chỉ sai kiểu (`var f = 1.0; f++`) thì là `TypeMismatchInExpression`.

---

## 8. `when {... -> 1; else -> 1.0}` có hợp lệ không?

**Q:**
`when {... -> 1; else -> 1.0}` thì có hợp lệ không (vì Int chuyển về Float nên type giống nhau)?

Int được phép đưa về Float nhưng không có chiều ngược lại đúng không: vị trí nào cần Int mà trả về Float thì là TypeMismatch đúng không?

**A:**
Đọc lại kỹ các phần sau:

- `mkotlin_specification.md` — mục When Expression (mọi nhánh phải cho giá trị cùng một kiểu; bắt buộc có `else`).
- `mkotlin-semantic_constraints_and_errors.md` — mục When (as an expression: every branch must yield the same type).
- `mkotlin_specification.md` — Rule 4.1 Assignment compatibility và Rule 4.3 Call compatibility (Int → Float widening; chiều ngược lại không được phép).

> Câu trả lời đã nằm trong các đoạn đó.

---

## 9. Int → Float widening có áp dụng cho `return` không?

**Q:**
Việc Int → Float widening có áp dụng cho `Return` không? Như trường hợp:

```kotlin
fun f(): Float { return 1 }
```

Thì là hợp lệ hay lỗi?

**A:**
Có — Int → Float áp dụng khi kiểm giá trị của `return` với kiểu trả về đã khai báo. Vì vậy:

```kotlin
fun f(): Float { return 1 }
```

là hợp lệ.

Chiều ngược lại vẫn không được:

```kotlin
fun g(): Int { return 1.0 } // TypeMismatchInStatement
```

**Tóm lại:** với kiểu trả về đã khai báo, `return e` được kiểm như đưa `e` vào vị trí kiểu đó — cho phép Int → Float, không cho Float → Int.

---

## 10. `when (1.0) {1 -> ...}` và `when (1) {1.0 -> ...}` có hợp lệ không?

**Q:**
`when (1.0) {1 -> ...}` và `when (1) {1.0 -> ...}` thì có hợp lệ không (được widen hai chiều như vậy không)?

**A:**
Đọc lại kỹ các phần sau:

- `mkotlin-semantic_constraints_and_errors.md` — mục When, Subject form (label phải khớp kiểu subject with Int/Float promotion).
- `mkotlin_specification.md` — mục Relational / Equality Expression (mixed Int/Float equality / numeric promotion).

> Câu trả lời đã nằm trong các đoạn đó.

---

## 11. Rule 5 về suy luận kiểu trả về — đệ quy và `return` trống lẫn có giá trị

**Q:**
Rule 5 vừa nói kiểu trả về suy từ "the first value-returning return statement", vừa nói nó là "a property of the whole body" và "All return statements must agree".

**a) Đệ quy không khai báo kiểu trả về:**

```kotlin
fun fact(n: Int) {
    if (n > 1) {
        return n * fact(n - 1)
    }
    return 1
}
```

**b) Hàm vừa có return trống vừa có return mang giá trị:**

```kotlin
fun f(n: Int) {
    if (n > 0) {
        return
    }
    return 5
}
```

Các trường hợp trên được coi là hợp lệ hay lỗi?

**A:**

**1. Đệ quy không khai báo kiểu trả về**

```kotlin
fun fact(n: Int) {
    if (n > 1) {
        return n * fact(n - 1)
    }
    return 1
}
```

Là hợp lệ. Kiểu trả về suy ra là `Int`.

"First value-returning return" là quy tắc neo kiểu; "property of the whole body" / "multiple internal passes" cho phép checker duyệt thân hàm đủ để xác định kiểu đó (ở đây từ `return 1` và kiểm `return n * fact(n - 1)` khớp), kể cả khi có lời gọi đệ quy.

**2. Vừa return trống vừa return có giá trị**

```kotlin
fun f(n: Int) {
    if (n > 0) {
        return
    }
    return 5
}
```

Là lỗi `TypeMismatchInStatement`.

Có `return 5` nên kiểu trả về không phải Unit (suy ra Int). Trong hàm không-Unit, `return` không kèm giá trị không được phép — các `return` phải thống nhất với kiểu đã suy/khai báo.

---

## 12. Node lỗi TypeCannotBeInferred cho UnaryOp, CallExpr, MemberAccess

**Q:**

**1. Về AST Node của lỗi TypeCannotBeInferred**

Trong Đặc tả có ví dụ: với `val c = a * b` (khi cả `a` và `b` đều unknowns), Node truyền vào lỗi sẽ là toàn bộ phép toán `BinaryOp`. Vậy với 2 trường hợp sau, node bị bắt lỗi sẽ là gì?

**a)**

```kotlin
fun main() {
    var a
    val c = -a
}
```

Lỗi sẽ được ném ra tại toàn bộ node `UnaryOp(-, Id(a))` hay sẽ bắt tại `Id(a)`?

**b)**

```kotlin
fun foo(x: Int) {}
fun main() {
    var a
    foo(-a)
}
```

Lời gọi `foo(-a)` sẽ thất bại. Quá trình suy luận sẽ ném lỗi tại node `CallExpr`, `UnaryOp`, hay `Id(a)`?

**2. Đối với biểu thức Member Access**

Khi trình biên dịch phân tích biểu thức `obj.m` trong đoạn code sau:

```kotlin
fun main() {
    var obj
    val x = obj.m
}
```

Đang phân vân 2 hướng xử lý lỗi:

- **Hướng 1:** Quăng lỗi `TypeCannotBeInferred` (tại `Id(obj)`) vì suy luận kiểu của toán hạng `obj` đã thất bại.
- **Hướng 2:** Quăng lỗi `TypeMismatchInExpression` (tại `MemberAccess`) theo đúng dòng luật riêng của Member Access.

Test sẽ ưu tiên bắt lỗi nào trong trường hợp này, và AST Node cụ thể truyền vào exception là gì?

**A:**
Ba trường hợp nêu đều rơi vào `TypeCannotBeInferred`. Node truyền vào exception là biểu thức khiến suy luận thất bại — cùng quy ước với ví dụ `a * b` → `BinaryOp(...)` trong mục Error Types / Type Inference Obligations.

**1a. `val c = -a`**

```
Type Cannot Be Inferred: UnaryOp(-, Id(a))
```

Unary `-` chấp nhận cả Int và Float, nên không neo được kiểu của `a`. Anchor "đối diện literal nguyên" chỉ áp dụng cho toán nhị phân `+ - * /`, không áp dụng cho unary.

**1b. `foo(-a)`**

```
Type Cannot Be Inferred: UnaryOp(-, Id(a))
```

Kiểu tham số của `foo` chỉ neo được khi argument là một identifier trần (ví dụ `foo(a)`). Với argument phức hợp `-a`, kiểu tham số không lan xuống operand. Lỗi xảy ra khi gõ kiểu cho `UnaryOp`, trước khi đối chiếu với tham số — không báo trên `CallExpr` và không báo trên `Id(a)` đơn lẻ.

**2. `val x = obj.m`**

```
Type Cannot Be Inferred: MemberAccess(Id(obj), m)
```

Member access không nằm trong các ngữ cảnh neo kiểu của var chưa annotation. Vì chưa có kiểu của `obj`, chưa đến bước kiểm "receiver phải là data class" — vì vậy không dùng `TypeMismatchInExpression` ở đây. `TypeMismatchInExpression` chỉ áp khi receiver đã có kiểu nhưng kiểu đó không phải data class, hoặc member không tồn tại trên kiểu đó.

**Tóm lại:** ưu tiên `TypeCannotBeInferred` khi var chưa được neo; node là biểu thức bao quanh chỗ suy luận thất bại (`UnaryOp` / `MemberAccess`), theo cùng quy ước với ví dụ `BinaryOp`.

---

## 13. `var a; if (a) {}` — node lỗi là `Id(a)` hay `If(...)`?

**Q:**

```kotlin
var a
if (a) {}
```

(hoặc biểu thức xuất hiện trong điều kiện hoặc subject của `while`/`for`/`when` tương tự) ⇒ là lỗi `Type Cannot Be Inferred: Id(a)` HAY `Type Cannot Be Inferred: If(...)`?

**A:**
Với

```kotlin
var a
if (a) { }
```

(và tương tự khi `a` xuất hiện trần trong điều kiện `while` / subject hoặc guard của `when`), lỗi là:

```
Type Cannot Be Inferred: Id(a)
```

Điều kiện / subject không thuộc các ngữ cảnh neo kiểu của var chưa annotation (gán, argument là identifier trần, return cả biểu thức, hoặc anchor literal trong toán nhị phân). Vì vậy không suy được kiểu của `a`.

Node truyền vào là `Id(a)` — đúng biểu thức khiến suy luận thất bại — **không phải** toàn bộ `If(...)`. Toàn bộ statement (`If(...)`, `While(...)`, ...) chỉ dùng khi điều kiện đã có kiểu nhưng không phải Boolean → khi đó mới là `TypeMismatchInStatement`.

---

## 14. Anchor kiểu cho `var a; var b = 1; b = a;` và `var b = a + 1.0`

**Q:**

```kotlin
var a; var b = 1; b = a;
```

⇒ Vậy có suy diễn ra được `a` kiểu Int không?

```kotlin
var b = a + 1.0
```

⇒ không neo được kiểu của `a` vì `1.0` là float không phải Int đúng không?

**A:**
Đọc lại kỹ các phần sau:

- `mkotlin_specification.md` — Type Inference, Rule 2.2 và 2.2.1 Inference contexts (đặc biệt bullet Assignment và Integer-literal anchor).
- `mkotlin-semantic_constraints_and_errors.md` — mục Type Inference Obligations (first usage của var, integer-literal anchor).

> Câu trả lời đã nằm trong các đoạn đó.

---

## 15. `var a; var b; a = b;` — hai unknown lẫn nhau thì bắt lỗi thế nào?

**Q:**

```kotlin
var a; var b; a=b;
```

Theo spec là lhs neo được cho rhs và rhs cũng neo được lhs thì bắt lỗi như thế nào?

**A:**
> **Lưu ý của giảng viên:** Phải đọc đề chứ sao lại hỏi để confirmation mà không đọc đề. Yêu cầu nghiêm túc đọc đề, khi hỏi phải chỉ ra sự mâu thuẫn trong mô tả đề. Lần sau hỏi confirmation nữa sẽ không được trả lời.

Đọc lại kỹ các phần sau:

- `mkotlin_specification.md` — Type Inference, Rule 2.2 (first usage là assignment `v = rhs`: kiểu của `v` lấy từ kiểu của `rhs`, và `rhs` phải checkable được) và 2.2.1 bullet Assignment (chỉ khi lhs đã có kiểu xác định thì mới kiểm/neo unknown trên rhs).
- `mkotlin-semantic_constraints_and_errors.md` — mục Type Inference Obligations (hai unknown không có anchor → `TypeCannotBeInferred`).

> Câu trả lời đã nằm trong các đoạn đó.

---

## 16. `When` statement khi subject không phải kiểu so sánh được

**Q:**

```
### When

- **Subject form:** `type(subject)` must be comparable (`Int`, `Float`, `Boolean`, `String`). Each label expression must match the subject type (with `Int`/`Float` promotion) -> else `TypeMismatchInExpression`. More than one `else` -> `Redeclared`-style structural error reported as `TypeMismatchInStatement` (impleme...
- **Conditionless form:** each guard must be `Boolean` -> else `TypeMismatchInExpression`.
- As an **expression**, every branch must yield the same type and an `else` is required -> else `TypeMismatchInExpression`.
```

Đoạn mô tả này chỉ nói rằng ném lỗi `TypeMismatchInExpression` khi nhãn của biểu thức không match với kiểu của subject. Nhưng nếu type của subject không phải là 1 type so sánh được thì đề không nói quăng lỗi gì. Là `TypeMismatchInStatement` hay `Expression`?

**A:**
Quan sát đúng: đoạn When chưa ghi rõ lỗi khi subject không comparable. Quy tắc áp dụng như sau.

**When statement** — subject không thuộc Int/Float/Boolean/String:

```
TypeMismatchInStatement
```

Node truyền vào là toàn bộ `When(...)` (cùng kiểu báo lỗi với điều kiện không-Boolean của `if`/`while`).

```kotlin
data class Point(x: Int, y: Int)
fun main() {
    val p = Point(1, 2)
    when (p) {    // TypeMismatchInStatement – When(...)
        else -> printInt(0)
    }
}
```

**When expression** — cùng ràng buộc subject; lỗi là `TypeMismatchInExpression`, node là `WhenExpr(...)`.

Còn label lệch kiểu subject (kể cả sau promotion Int/Float) vẫn là `TypeMismatchInExpression` như đoạn mô tả đã viết.

---

## 17. `val p = Vec(1, 2)` khi `Vec` chưa khai báo — UndeclaredFunction hay UndeclaredClass?

**Q:**
Ví dụ:

```kotlin
fun main() {
    val p = Vec(1, 2)
}
```

Trong trường hợp `Vec` chưa hề khai báo trước đó, checker nên xử lý như nào?

- Báo lỗi `UndeclaredFunction` vì theo spec phần Expressions - Calls có ghi: "A call whose name is completely unknown is treated as an unknown function call"
- Hay là báo lỗi `UndeclaredClass` giống như `test_005_undeclared_class` đang expect (có thể là do ngầm định dựa vào chữ cái đầu viết hoa?)

Nếu theo hướng testcase thì có được sử dụng mẹo check chữ cái hoa/thường để phân biệt lỗi không?

**A:**
Đọc lại kỹ các phần sau trong `mkotlin-semantic_constraints_and_errors.md`:

- **Error Types** — mục 3 UndeclaredFunction và mục 4 UndeclaredClass;
- **Expressions** — bullet Calls `f(args)` (kể cả câu "Resolution is based on declarations, not identifier capitalization");
- **Worked Examples** — UndeclaredFunction / UndeclaredClass;
- `tests/test_checker.py` — `test_005_undeclared_class` (hiện dùng vị trí kiểu, không còn dạng `Vec(1, 2)`).

> Câu trả lời đã nằm trong các đoạn đó.

---

## 18. Đệ quy không neo được kiểu trả về: `fun f() { return f() }`

**Q:**

```kotlin
fun f() {
    return f()
}
```

Vì kiểu trả về của `f()` phụ thuộc vào chính kiểu trả về đang được suy luận, trong hàm cũng không có `return` nào khác để làm type anchor. Theo hiểu thì nó sẽ báo `TypeCannotBeInferred`.

Tuy nhiên tài liệu không quy định node nào sẽ làm context lỗi trong trường hợp trên. Nếu đúng là lỗi này thì node truyền vào sẽ là `CallExpr(f, [])`, `Return(CallExpr(...))` hay `FuncDecl`?

**A:**
Hiểu đúng hướng: chương trình

```kotlin
fun f() {
    return f()
}
```

báo `TypeCannotBeInferred`. Không có kiểu trả về khai báo; return value–returning duy nhất lại phụ thuộc chính kiểu đang suy luận, và không còn return/neo nào khác — kể cả multi-pass cũng không xác định được kiểu (không suy ra Unit vì đã có return kèm giá trị).

Node truyền vào exception là:

```
Return(CallExpr(f, []))
```

tức value–returning return đầu tiên — chỗ lẽ ra neo kiểu trả về theo Rule 5. Không dùng `CallExpr` đơn lẻ hay toàn bộ `FuncDecl`.

---

## 19. `var x` không annotation, không initializer, không dùng — và hợp nhất kiểu nhánh `when` expression

**Q:**

**1. Biến không có type annotation và initializer**

Ví dụ:

```kotlin
fun main() {
    var x
}
```

Trong trường hợp `x` không có annotation, không có initializer và cũng không được sử dụng sau đó, checker nên xử lý như thế nào?

- Chương trình hợp lệ vì không có ngữ cảnh yêu cầu biết type của `x`;
- Hay phải báo `TypeCannotBeInferred` ngay tại declaration;
- Hay chỉ báo lỗi khi `x` được sử dụng lần đầu trong một ngữ cảnh không thể suy type?

Nếu phải báo `TypeCannotBeInferred`, node được truyền vào lỗi nên là `VarDecl` hay một node khác?

**2. Hợp nhất kiểu của các nhánh `whenExpr`**

Ví dụ:

```kotlin
fun main() {
    val x = when (1) {
        1 -> 10
        else -> 20.0
    }
}
```

Hai nhánh lần lượt có type Int và Float.

Checker nên:

- Cho phép numeric promotion và suy type của `WhenExpr` thành Float;
- Hay yêu cầu tất cả branch phải có type giống nhau hoàn toàn và báo `TypeMismatchInExpression` trên `WhenExpr`?

**A:**

**1. `var x` không annotation, không initializer, không được dùng**

```kotlin
fun main() {
    var x
}
```

Đây là lỗi `TypeCannotBeInferred`. Kiểu của var không annotation được suy từ first usage; nếu không có usage nào neo được kiểu thì không có quy tắc nào "fix" biến đó — không coi chương trình hợp lệ chỉ vì không ai đọc `x`.

Node truyền vào exception là declaration:

```
VarDecl(var, x, None, None)
```

**2. Hợp nhất kiểu các nhánh whenExpr**

Đọc lại:

- `mkotlin_specification.md` — mục When Expression (every branch must produce a value of the same type);
- `mkotlin-semantic_constraints_and_errors.md` — mục When, as an expression (every branch must yield the same type → else `TypeMismatchInExpression`).

> Câu trả lời cho phần này đã nằm trong các đoạn đó.