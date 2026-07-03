# Forum Q&A — MKotlin Specification

## Q1

> "If a function returns a data class value, its result can be used in member access: `getPoint().x` is valid when `getPoint()` returns a type with member `x`."

nhưng mà đề cương có ghi độ ưu tiên của member access cao hơn function call nên em không biết có nhầm lẫn không ạ do phải access member trước khi gọi hàm ạ.

## A1

Chào em,

Cảm ơn em đã đặt câu hỏi. Đây là một chỗ dễ nhầm khi mới học precedence, nhưng hai đoạn trong đề không hề mâu thuẫn nhau.

### `getPoint().x` được hiểu thế nào?

Biểu thức `getPoint().x` được parse thành:

```
(getPoint()).x
```

Nghĩa là:

- Gọi hàm `getPoint()` trước → nhận một giá trị kiểu data class.
- Sau đó truy cập member `.x` trên kết quả của lời gọi hàm đó.

Điều này khớp với mô tả trong đề:

> "The left-hand side may be any expression that evaluates to a data class type"

— vế trái của `.` có thể là một biểu thức bất kỳ, kể cả lời gọi hàm.

### Vì sao không phải "access member trước khi gọi hàm"?

Toán tử `.` là toán tử hậu tố (postfix): nó luôn cần một biểu thức hoàn chỉnh ở bên trái.

Trong `getPoint().x`, bên trái dấu `.` không phải là `getPoint` đơn lẻ, mà là cả `getPoint()` — một lời gọi hàm đã hoàn chỉnh. Vì vậy parser sẽ:

- ghép `()` với `getPoint` → `getPoint()`
- rồi ghép `.x` với kết quả trên → `(getPoint()).x`

`.` có độ ưu tiên cao hơn `()` không có nghĩa là `.` được áp dụng trước `()` trong chuỗi token `getPoint ( ) . x`. Nó chỉ quy định cách nhóm các toán tử postfix khi có nhiều toán tử cùng xuất hiện.

Ví dụ, `obj.getValue()` được hiểu là `(obj.getValue)()` — truy cập member `getValue` của `obj`, rồi gọi kết quả đó như một hàm — chứ không phải `obj.(getValue())`.

### Em nên đọc lại những phần nào?

- Member Access (mục Data Class Variable Declaration and Construction): đoạn nói vế trái của `.` có thể là any expression, và ví dụ `getPoint().x`.
- Operator Precedence and Associativity (mục Expressions): bảng thứ tự ưu tiên — `.` cao hơn `()` (call).
- Grammar Summary cuối đặc tả: nhóm postfix gồm `++`, `--`, và `()` (call), trong khi member access `.` đứng trên nhóm đó.

Ba phần này bổ sung cho nhau: precedence quy định cách ghép toán tử, còn mô tả member access quy định vế trái của `.` là một biểu thức — hai ý này cùng dẫn đến `(getPoint()).x`.

---

## Q2

Dạ thầy ơi, em muốn xác nhận một chút về phần Statement Termination ạ. Theo spec thì câu lệnh có thể kết thúc bằng 'natural end of the construct, such as a closing brace'. Vậy nếu em có một đoạn code viết dồn trên 1 dòng như vầy: `fun main() { continue }` (hoàn toàn không có dấu xuống dòng `\n` hay dấu `;` ở cuối chữ `continue`), thì trình biên dịch vẫn tính là hợp lệ đúng không thầy?

## A2

Chào em,

Em hiểu đúng rồi. Với ví dụ:

```kotlin
fun main() { continue }
```

(viết trên một dòng, không có `\n` hay `;` sau `continue`)

thì về mặt cú pháp (phạm vi BTL 1), trình biên dịch vẫn coi là hợp lệ.

### Giải thích ngắn gọn

Theo đặc tả, câu lệnh kết thúc khi gặp một trong hai trường hợp:

- Newline (`\n`), hoặc
- Điểm kết thúc tự nhiên của cấu trúc — ví dụ dấu `}` đóng block

Trong `fun main() { continue }`, câu lệnh `continue` nằm trong block `{ ... }` và kết thúc ngay trước `}`. Vì vậy không cần thêm newline hay dấu `;` sau `continue`.

Dấu `;` chỉ cần khi em muốn viết nhiều câu lệnh trên cùng một dòng, ví dụ:

```kotlin
fun main() { val x = 10; val y = 20 }
```

Còn nếu block chỉ có một câu lệnh thì không cần separator sau câu lệnh đó.

---

## Q3

Dạ chào thầy, em thấy trong specification về phần IF statement: if/else có thể sử dụng như expression, em muốn xác nhận lại một chút về if expression ạ.

Theo em hiểu If Expression là nó phải tạo ra giá trị (produce a value). Do đó, trình phân tích sẽ ép nó vào luật Expression (bắt buộc có else) trong các ngữ cảnh đang cần giá trị như: nằm ở vế phải phép gán, nằm trong biểu thức toán học (VD: `y = 10 + if (a > b) 1 else 0`), làm đối số truyền vào hàm, hoặc đi sau lệnh return... Dạ cho em hỏi em hiểu như vậy là đúng với phần If expression này chưa ạ?

Với trường hợp lệnh đứng độc lập trong hàm như thế này:

- `fun main() { if (x > 0) printInt(1) else printInt(0) }`
- `fun main() { if (x > 0) 1 }`

Vì nó không gán cho ai (không produce a value cho ngữ cảnh bên ngoài), nên nó sẽ được parse là một Statement đúng không ạ? Và nếu đã là Statement thì nhánh else lúc này là không bắt buộc (tùy chọn) đúng không thầy?

Trong MKotlin, If Expression có cho phép thân của nó chứa khối lệnh `{ }` không thầy? (Ví dụ: `val x = if (a) { 1 } else { 2 }`).

## A3

Chào em,

Em hiểu đúng về sự phân biệt giữa if statement và if expression trong MKotlin.

### 1. If expression — khi nào dùng?

Theo đặc tả, if/else dùng như expression khi nó phải tạo ra giá trị (produce a value): cả hai nhánh đều là biểu thức cùng kiểu, và else là bắt buộc.

Ví dụ trong spec:

```kotlin
val m = if (a > b) a else b
```

Về parser (BTL 1), khi `if` xuất hiện ở ngữ cảnh cần expr — về phải phép gán, trong biểu thức toán học, đối số hàm, sau return, v.v. — nó được parse theo luật if expression (nhánh then/else là expr, có else).

Em liệt kê các ngữ cảnh đó là chính xác.

### 2. Hai ví dụ if đứng độc lập trong hàm

**a)** `fun main() { if (x > 0) printInt(1) else printInt(0) }`

Đúng — đây là if statement: `if` nằm trong danh sách câu lệnh của block, hai nhánh là statement (`printInt(...)` là expression statement). `else` có ở đây nhưng không bắt buộc ở dạng statement.

**b)** `fun main() { if (x > 0) 1 }`

Cũng đúng — vẫn là if statement, nhánh then là expression statement (literal `1`). Vì không nằm trong ngữ cảnh cần giá trị nên không parse thành if expression, và else là tùy chọn.

Lưu ý: cú pháp hợp lệ không đồng nghĩa chương trình "có ý nghĩa" về ngữ nghĩa; phần đó thuộc BTL 3.

### 3. If expression có cho phép thân `{ }` không?

Không. Trong MKotlin, if expression có dạng:

```
if (<expr>) <expr> else <expr>
```

Hai nhánh phải là expr, không phải stmt. Khối `{ ... }` là block statement — thuộc luật statement, không thuộc primary expression.

Vì vậy:

```kotlin
val x = if (a) { 1 } else { 2 } // không hợp lệ về cú pháp
```

Nếu cần khối lệnh nhiều dòng, dùng if statement:

```kotlin
if (flag) {
    printInt(1)
} else {
    printInt(0)
}
```

Đây là mẫu if statement có block, không phải if expression.

So sánh với when: when expression dùng expr sau `->`; when statement dùng stmt — cùng nguyên tắc phân biệt theo ngữ cảnh.

---

## Q4

Dạ em chào thầy,

Tại Mục 3. Cấu trúc từ vựng -> Kết thúc câu lệnh, Đặc tả có ghi:

> "Một câu lệnh kết thúc tại ký tự xuống dòng (hoặc tại điểm kết thúc tự nhiên của cấu trúc đó, chẳng hạn như dấu ngoặc nhọn đóng)."

Tuy nhiên, trong thực tế code, lập trình viên có thể xuống dòng ngay trước khi mở ngoặc nhọn của một khối lệnh. Ví dụ đối với khai báo hàm `fun` hoặc lệnh `if`:

```kotlin
// Cách 1: Ngoặc nhọn mở trên cùng một dòng (Giống các ví dụ trong Đặc tả)
fun main() {
    printInt(1)
}

if (a > 0) {
    printInt(1)
}

// Cách 2: Có ký tự NEWLINE nằm ngay trước dấu ngoặc nhọn mở
fun main()
{
    printInt(1)
}

if (a > 0)
{
    printInt(1)
}
```

Thầy cho em hỏi đối với Cách 2 thì Parser của MKotlin sẽ xử lý như thế nào ạ?

Báo lỗi Syntax Error ngay tại ký tự `\n` (do bắt buộc dấu `{` phải nằm trên cùng một dòng với khai báo cha).

Hay vẫn Parse thành công (coi `\n` lúc này chỉ là khoảng trắng vô nghĩa vì cấu trúc fun/if vẫn đang đợi điểm kết thúc tự nhiên là dấu `}`).

Em cảm ơn thầy ạ.

## A4

Chào em,

Đây là chỗ dễ nhầm vì spec vừa coi newline là whitespace (mục Character Set), vừa dùng newline để kết thúc/tách câu lệnh (mục Statement Termination). Câu trả lời phụ thuộc cấu trúc đang parse, không có một quy tắc chung "mọi `\n` trước `{` đều hợp lệ hoặc đều lỗi".

### Nguyên tắc chung

Trong MKotlin, `\n` là token NEWLINE — parser chỉ chấp nhận khi grammar có `NEWLINE*` hoặc `sep` (newline / `;`). Space và tab thì lexer bỏ qua; newline thì không.

Mục Statement Termination ("kết thúc tại newline hoặc `}`") áp dụng khi parser đang xử lý danh sách câu lệnh và cần biết một câu lệnh đã kết thúc chưa. Nó không có nghĩa mọi `\n` trước `{` đều gây lỗi, cũng không có nghĩa mọi `\n` đều bị bỏ qua.

### Cách 2 với `if` — parse thành công

```kotlin
if (a > 0)

{
    printInt(1)
}
```

Hợp lệ. Luật if statement có dạng:

- `if (<expr>) <statement>`
- `if (<expr>) <statement> else <statement>`

Sau điều kiện, grammar cho phép `NEWLINE*` rồi mới tới `<statement>`. Khối `{ ... }` là một `<statement>` (block statement), nên `\n` giữa `)` và `{` được chấp nhận.

Tương tự, `while` và `for` cũng cho phép `NEWLINE*` trước phần thân câu lệnh.

### Cách 2 với `fun` — báo lỗi cú pháp

```kotlin
fun main()

{
    printInt(1)
}
```

Không hợp lệ. Khai báo hàm có dạng:

```
fun <identifier>(<parameter_list>): <return_type> {
<statement_list>
}
```

Phần `{ ... }` (block thân hàm) phải nối trực tiếp sau `)` hoặc sau `<return_type>`. Grammar không có `NEWLINE*` giữa phần đầu hàm và `{`, nên parser gặp `\n` sẽ báo syntax error (không mong đợi token NEWLINE tại vị trí đó).

Ví dụ hợp lệ:

```kotlin
fun main() {
    printInt(1)
}

fun main(): Unit {
    printInt(1)
}
```

Đây là mẫu statement có block, không phải if expression.

So sánh với when: when expression dùng expr sau `->`; when statement dùng stmt — cùng nguyên tắc phân biệt theo ngữ cảnh.

---

## Q5

trong when statement có luôn yêu cầu có ít nhất 1 branch không ạ?

ví dụ `when (a) {}` thì nó có hợp lệ hay không?

em mong thầy giải đáp giúp em ạ

## A5

Với when statement (phạm vi BTL 1 — parser), không yêu cầu phải có ít nhất một branch.

Ví dụ:

```kotlin
when (a) {}
```

là hợp lệ về mặt cú pháp. Parser chấp nhận danh sách branch rỗng bên trong `{ }`.

### Giải thích ngắn

Trong đặc tả, when statement có hai dạng (subject form và conditionless form). Đối với dạng statement:

- `else` là tùy chọn (không bắt buộc).
- Đặc tả không quy định phải có ít nhất một nhánh `->`.

Vì vậy `when (a) { }` — không có nhánh nào, cũng không có else — vẫn parse thành công. Khi chạy, khối when không làm gì và chương trình tiếp tục sau `}`.

Cách suy luận tương tự block rỗng: đặc tả nói rõ `{ }` (danh sách câu lệnh rỗng) là hợp lệ; when statement cũng cho phép danh sách branch rỗng.

### Lưu ý: when statement ≠ when expression

Đừng nhầm với when expression (dùng ở ngữ cảnh cần giá trị, ví dụ `val x = when (...)`). Ở dạng expression, mọi branch phải tạo giá trị cùng kiểu và else là bắt buộc — quy tắc chặt hơn when statement.

Câu hỏi của em về `when (a) {}` là về when statement, nên áp dụng quy tắc parser ở trên.

### Khi viết grammar

Trong `MKotlin.g4`, luật cho danh sách branch của when statement nên cho phép không có branch nào (tương đương `whenBranch*` — zero or more).

---

## Q6

trong spec member access có đề cập "If a function returns a data class value, its result can be used in member access: `getPoint().x` is valid when `getPoint()` returns a type with member `x`." Nhưng trong thứ tự ưu tiên MAC lại có ưu tiên cao hơn call thì nó sẽ không hợp lệ (mâu thuẫn với cái trên). Mong thầy giải đáp giúp em với ạ

## A6

Hai đoạn em trích dẫn không mâu thuẫn với nhau. Em đang hiểu nhầm ý nghĩa của "độ ưu tiên cao hơn" trong bảng precedence.

Em vui lòng đọc lại kỹ các phần sau trong đặc tả:

- Type System → Data Class → Member Access — đặc biệt câu "The left-hand side may be any expression that evaluates to a data class type" và ví dụ `getPoint().x`.
- Expressions → Operator Precedence and Associativity — bảng thứ tự ưu tiên (`.` cao hơn `()` call).

Sau khi đọc lại hai mục trên, em tự suy luận xem `getPoint().x` được parse như thế nào và vì sao. `.` có độ ưu tiên cao hơn `()` không có nghĩa là "phải access member trước khi gọi hàm". Chúc em làm bài tốt.

---

## Q7

Unclosed strings are detected if the string literal is not closed before encountering a newline, carriage return, or end of file.

A line comment ignores all characters from `//` to the end of the current line.

carriage return (the ASCII CR, `\r`) and newline (the ASCII LF, `\n`) are whitespace characters. The `\n` is used as the newline character in MKotlin.

-> Thầy cho em hỏi "to the end of the current line" ở ý 2 thì có tính carriage return không ạ.

-> Mình có thể xem carriage return như newline và không "skip" không ạ (vì ý 1 đang có ý nghĩa `\r` cũng là newline nhưng ý 3 lại ghi chỉ xem `\r` như white space).

Em xin cảm ơn thầy giải đáp ạ.

## A7

Chào em,

Hai ý em hỏi không mâu thuẫn nếu hiểu đúng vai trò của `\r` trong từng ngữ cảnh lexical.

### 1. Line comment — "to the end of the current line" có tính `\r` không?

Có. "Hết dòng" nghĩa là gặp `\n` hoặc `\r` (kể cả `\r\n` trên Windows). Phần `//` đến trước ký tự kết thúc dòng đó bị bỏ qua; `\r` và `\n` không nằm trong comment.

Ví dụ: `val x = 1 // comment\r\n` — comment kết thúc tại `\r`.

### 2. `\r` có được coi như NEWLINE và "không skip" không?

Không hoàn toàn như vậy. Trong MKotlin, `\r` và `\n` cùng được liệt kê là whitespace để định nghĩa dòng trong source, nhưng lexer xử lý chúng khác nhau tùy ngữ cảnh:

| Ngữ cảnh | `\r` được xử lý thế nào |
|---|---|
| Line comment | Kết thúc comment (cùng với `\n`) |
| Unclosed string | Kết thúc chuỗi chưa đóng (cùng với `\n`, EOF) |
| Token NEWLINE (parser) | Chủ yếu từ `\n`; `\r\n` được coi là một kết thúc dòng (`\r` tùy chọn trước `\n`) |
| Whitespace bị skip | Chỉ space, tab, form feed — không gồm `\r` đơn lẻ |

Tóm lại:

- `\r` không bị skip như space/tab.
- `\r` không luôn tương đương token NEWLINE của parser.
- `\r` có vai trò kết thúc dòng trong comment và trong xử lý lỗi chuỗi chưa đóng.

Câu "`\n` is used as the newline character in MKotlin" nghĩa là ký tự xuống dòng chuẩn và token NEWLINE của parser dựa trên `\n` (có thể kèm `\r` trong `\r\n`). Điều đó không có nghĩa `\r` chỉ là whitespace vô nghĩa ở mọi nơi.

---

## Q8

```
when () {
<value_1> -> 
<value_2>, <value_3> -> 
...
else -> 
}
```

=> sau mỗi statement này cần separator (newline hoặc `;`) không ạ.

## A8

Chào em,

**Không bắt buộc** — sau `<statement>` của mỗi nhánh `when`, separator (newline hoặc `;`) là **tùy chọn**, không phải bắt buộc.

### Giải thích

Mỗi nhánh `when` có dạng:

`<labels> -> <statement> /* sep tùy chọn ở đây */`

Phần **sep** sau `<statement>` là **không bắt buộc** (`sep*`: không hoặc nhiều separator). Nhánh tiếp theo bắt đầu bằng nhãn mới (hoặc `else`), không cần separator để "kết thúc" nhánh trước.

### Ví dụ

Cả hai đều hợp lệ về cú pháp:

```kotlin
when (day) {
    1 -> printInt(1)
    2, 3 -> printInt(2)
    else -> printInt(0)
}
```

```kotlin
when (day) { 1 -> printInt(1) 2, 3 -> printInt(2) else -> printInt(0) }
```

(Nhánh trên cùng một dòng — không có newline / `;` giữa các nhánh.)

### So sánh với danh sách câu lệnh thông thường

Trong block `{ ... }` hoặc thân hàm, các câu lệnh phải được tách bằng ít nhất một sep.

Trong `when { ... }`, các nhánh (whenBranch) là cấu trúc riêng — separator sau `<statement>` mỗi nhánh không bắt buộc.

Chúc em làm bài tốt.

---

## Q9

Thầy cho em hỏi có bắt buộc giữa hai khai báo liên tiếp (funcDecl và/hoặc dataClassDecl) luôn phải có ít nhất một sep (dấu `;` hoặc newline) hay không ạ?

Em xin cảm ơn thầy ạ.

## A9

Chào em,

Có — giữa hai khai báo liên tiếp (dataClassDecl và/hoặc funcDecl) bắt buộc phải có ít nhất một sep (newline hoặc `;`).

### Ví dụ

```kotlin
data class Point(x: Int, y: Int)

fun main() {}
```

Hợp lệ — có newline giữa hai khai báo.

```kotlin
data class Point(x: Int, y: Int); fun main() {}
```

Hợp lệ — dùng `;` làm separator.

```kotlin
data class Point(x: Int, y: Int)fun main() {}
```

Không hợp lệ — thiếu sep giữa `)` và `fun`.

### Lưu ý

Một khai báo đơn lẻ không cần sep trước hay sau (trừ newline đầu file nếu có — program cho phép `NEWLINE*` trước declList).

Quy tắc này áp dụng ở cấp chương trình (top-level), khác với quy tắc tách câu lệnh bên trong block hàm.

Chúc em làm bài tốt.

---

## Q10

A block comment starts with `/*` and ignores all characters (except EOF) until it reaches `*/` ⇒ Nếu file không ghi `*/` mà đã hết file thì mình cho là ERROR_TOKEN đúng không ạ

## A10

Chào em,

Không — trường hợp `/*` mà hết file chưa gặp `*/` không được quy định là ERROR_TOKEN trong đặc tả MKotlin.

### Vì sao?

Lexical Error Tokens chỉ liệt kê đúng ba loại lỗi lexer:

- `ERROR_TOKEN` — ký tự không nhận diện được
- `UNCLOSE_STRING`
- `ILLEGAL_ESCAPE`

Không có token riêng cho block comment chưa đóng.

Mục Comment mô tả block comment "ignores all characters (except EOF) until it reaches `*/`" — ý "except EOF" là comment không thể kéo dài qua EOF; không quy định phải phát ERROR_TOKEN khi gặp EOF.

Yêu cầu BTL 1 (README) về lỗi lexical tập trung vào ba loại trên và các trường hợp như unclosed string, illegal escape — không yêu cầu xử lý riêng unclosed block comment.

### Hành vi lexer thực tế

Với luật block comment dạng `/* ... */` (skip khi khớp đủ `*/`), nếu không có `*/` thì luật comment không khớp. Lexer sẽ tiếp tục tokenize các ký tự sau đó theo luật thông thường (ví dụ `/`, `*` có thể thành toán tử), không tự động báo ERROR_TOKEN tại EOF chỉ vì thiếu `*/`.

---

## Q11

Dạ thầy ơi cho em hỏi là đối với string literal thì kí tự newline có được tính là một phần của chuỗi không ạ hay là nó sẽ báo lỗi Unclosed String ạ?

Ví dụ:

```kotlin
val s = "abc
def"
```

Thì chuỗi này có hợp lệ không thầy? Em cảm ơn thầy.

## A11

Chào em,

Trong MKotlin, ví dụ của em không hợp lệ và lexer sẽ báo lỗi Unclosed string.

### Giải thích

Theo quy tắc xử lý chuỗi (đã trích dẫn ở câu trước):

> "Unclosed strings are detected if the string literal is not closed before encountering a newline, carriage return, or end of file."

Ký tự xuống dòng (`\n`) không được phép nằm trực tiếp bên trong một chuỗi bình thường (single-line string literal). Khi lexer đang parse chuỗi mà gặp ký tự xuống dòng trước khi thấy dấu `"` đóng chuỗi, nó sẽ dừng lại và báo lỗi chuỗi chưa đóng ngay tại dòng đó.

### Cách xử lý nếu muốn có newline trong chuỗi

Nếu muốn chuỗi chứa ký tự xuống dòng, em phải dùng mã escape:

```kotlin
val s = "abc\ndef"
```

(Chuỗi này viết trên một dòng, ký tự `\n` là hai ký tự `\` và `n` trong source code, khi chạy mới đổi thành ký tự xuống dòng thực tế). MKotlin không hỗ trợ chuỗi nhiều dòng (multi-line string / triple-quoted string `"""..."""`) như Kotlin thực tế, nên kiểu viết xuống dòng trực tiếp trong mã nguồn như ví dụ của em chắc chắn là lỗi cú pháp.

Chúc em làm bài tốt.
