# Forum Q&A — CallExpr, Grammar vs AST, Type Node __repr__

## Q1: Chênh lệch giữa Grammar và AST Node ở CallExpr

**Q:**
Dạ chào thầy,

Em có một thắc mắc về sự chênh lệch giữa Grammar và AST Node ở phần CallExpr ạ. Trong Spec, luật gọi hàm được định nghĩa là `<postfix_expression> (<argument_list>)`, tức là cho phép vế gọi hàm là một biểu thức. Nhưng trong file nodes.py, class CallExpr lại yêu cầu name truyền vào phải là kiểu str.

Thầy cho em hỏi là với sự khác biệt này, tụi em nên xử lý việc khởi tạo node CallExpr như thế nào ạ?

**A:**
Chào em,

Hai mô tả không mâu thuẫn — chúng phục vụ hai mục đích khác nhau.

**Grammar vs AST**

Trong grammar (BTL 1), `()` là toán tử postfix trên `<postfix_expression>` để parser nhóm đúng precedence/associativity (cùng nhóm với `.`, `++`, `--`).

Trong AST (BTL 2), CallExpr chỉ biểu diễn gọi hàm hoặc gọi constructor — hai dạng này trong MKotlin luôn có dạng `<identifier>(...)`, nên name là str.

Docstring của CallExpr trong nodes.py và mục General Rules trong mkotlin-ast_representation.md đều nói rõ điều này.

**Cách khởi tạo CallExpr**

Khi visit luật call postfix (`postfixExpr LPAREN argList? RPAREN`):

- Nếu vế trái ngay trước `()` là identifier → tạo `CallExpr(tên_identifier, danh_sách_args)`.
- Nếu vế trái là biểu thức postfix khác → không nhét vào CallExpr.name; thay vào đó gom bằng node postfix tương ứng.

Ví dụ:

| Source | AST |
|---|---|
| `printInt(42)` | `CallExpr("printInt", [IntLit(42)])` |
| `Point(1, 2)` | `CallExpr("Point", [IntLit(1), IntLit(2)])` |
| `getPoint().x` | `MemberAccess(CallExpr("getPoint", []), "x")` |

Ở `getPoint().x`, `()` gắn vào `getPoint` trước → `CallExpr("getPoint", [])`; sau đó `.x` là MemberAccess, không phải call với callee kiểu Expr.

Em không cần:
- Đổi `CallExpr.name` thành `Expr`.
- Coi mọi lần xuất hiện `()` trong parse tree đều phải thành CallExpr.

CallExpr chỉ dùng cho gọi hàm/constructor theo tên. Các postfix khác dùng node riêng (MemberAccess, PostfixOp, ...).

Em nên đọc lại:
- mkotlin-ast_representation.md → General Rules — function/constructor calls → `CallExpr(name, [args...])`
- nodes.py → class CallExpr — docstring về function call / constructor call
- Spec → Function Call Expression — dòng "The usual cases are `<identifier>(...)`"
- Spec → Operator Precedence and Associativity — bảng postfix và ví dụ `getPoint().x`

Chúc em làm bài tốt.

---

## Q2: Input `CountPoint()(1)` — sinh AST như thế nào? Đổi `name` thành `Expr`?

**Q:**
Thầy cho em hỏi với input là `CountPoint()(1)` thì mình sẽ sinh cây AST như thế nào ạ. Tại vì `CountPoint()` không phải name để tạo ra class CallExpr

```python
@dataclass
class CallExpr(Expr):
    """A function call or a data-class constructor call.
    
    The two are syntactically identical; the static checker resolves which
    one `name` refers to.
    """
    
    name: str
    args: List[Expr] = field(default_factory=list)
    
    def __repr__(self):
        return f"CallExpr({self.name}, [{', '.join(repr(a) for a in self.args)}])"
```

Nếu như mình chuyển `name -> name: Expr` thì sao ạ. Tại vì `object.getValue()` -> `(object.getValue) ()` -> vế trái của `()` là Expr chứ không phải string ạ. Các trường hợp tương tự như là `(x+1)()`, `1()`

**A:**
Chào em,

Em không được (và không cần) đổi `CallExpr.name` thành `Expr`. Node này trong nodes.py đã cố định: `name: str` — dùng cho gọi hàm hoặc gọi constructor theo tên (`printInt(...)`, `Point(...)`).

Phân biệt hai tầng:

- Grammar (BTL 1): `()` là postfix trên `<postfix_expression>` để nhóm precedence (cùng nhóm với `.`, `++`, `--`).
- AST (BTL 2): chỉ khi callee là identifier mới tạo `CallExpr("tên", [args...])`.

Với các ví dụ em nêu:

- `printInt(42)` → `CallExpr("printInt", ...)`
- `getPoint().x` → gọi `getPoint` trước, rồi member `.x` (xem bảng postfix trong Spec)
- `object.getValue()` → `.` là member access (property), không phải method; không map thành CallExpr với callee kiểu Expr
- `(x+1)()`, `1()` → không có testcase cho các dạng này vì chúng không phải dạng gọi hàm/constructor hợp lệ trong MKotlin

Em nên đọc lại:
- nodes.py → docstring CallExpr (`name: str`, function/constructor call)
- mkotlin-ast_representation.md → General Rules — `CallExpr(name, [args...])`
- Spec → Function Call Expression — "The usual cases are `<identifier>(...)`"
- Spec → Member Access và Operator Precedence — ví dụ `getPoint().x`

Chúc em làm bài tốt.

---

## Q3: `__repr__` của các Type node (IntType, FloatType, ...) không có dấu ngoặc

**Q:**
IntType, FloatType, BoolType, StringType, UnitType có `__repr__` không có dấu ngoặc (`"IntType"`, không phải `"IntType()"`) — khác với ví dụ minh họa trong mkotlin-ast_representation.md. Cho em hỏi là mình dùng đúng theo file nodes.py là `"IntType"` hay sẽ sửa lại theo đặc tả là `"IntType()"` ạ. Do web đang bị lỗi khi up ảnh nên em không up lên được để minh họa ạ

**A:**
Chào em,

Em không cần (và không được) sửa nodes.py — đây là file em không nộp. Việc `__repr__` in ra `"IntType"` hay `"IntType()"` là việc của thầy/hệ thống chấm.

Việc của em chỉ là sinh đúng cây AST: tạo đúng node từ nodes.py (ví dụ `nodes.IntType()`, `nodes.FloatType()`, ...) và gắn đúng vào cấu trúc chương trình.

Em không cần lo khớp chuỗi minh họa trong mkotlin-ast_representation.md với `__repr__`; cứ dùng đúng các class type đã cho là được.

Chúc em làm bài tốt.