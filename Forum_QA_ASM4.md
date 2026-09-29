---
title: Forum Q&A - ASM4 (Emitter / Jasmin Code Generation)
tags: [mkotlin, forum-qa, codegen, jasmin, emitter, asm4]
course: Principles of Programming Languages
type: forum-qa
---

# Forum Q&A - ASM4 (Emitter / Jasmin Code Generation)

## Mục lục

- [[#Thông báo từ thầy]]
- [[#Q1 - Tham số frame bị thiếu và hiệu ứng stack của emit_cmp_int]]

---

## Thông báo từ thầy

> [!warning] Cảnh báo về việc print_out trực tiếp thay vì dùng jasmin_code
> Gửi các bạn,
>
> Thầy có xem sơ qua các bài tập lớn các bạn đã nộp. Thầy cảnh báo trước, hiện tại có rất nhiều bạn print_out trực tiếp code trong emitter hoặc code generator mà không gọi qua lớp jasmin_code. Điều này là hết sức nguy hiểm, khi chấm thầy sẽ thay thành dạng bytecode khác dùng ký pháp tương đương jasmin thì toàn bộ bài của các bạn sẽ không chạy được.
>
> Thầy yêu cầu các bạn phải làm đúng như tinh thần framework đã đề ra.
>
> Duy./.

---

## Q1 - Tham số frame bị thiếu và hiệu ứng stack của emit_cmp_int

> [!question] Bùi Trịnh Nguyên Khải - 3 ngày trước
> Dưới đây là toàn bộ nội dung văn bản từ hình ảnh của bạn:
>
> BÀI VIẾT GỐC
>
> Bùi Trịnh Nguyên Khải
>
> 3 ngày trước
>
> Dạ em chào thầy ạ.
>
> Khi đọc file emitter.py và jasmin_code.py, em có những thắc mắc sau ạ.
>
> Em thấy rằng những hàm sau đây không có tham số frame nhưng frame lại được sử dụng trong thân hàm ạ:
>
> ```python
> class Emitter:
>     ...
>     def emit_if_false(self, label: int) -> str:
>         frame.pop()
>         return self.jvm.emitIFEQ(label)
>
>     def emit_if_true(self, label: int) -> str:
>         frame.pop()
>         return self.jvm.emitIFNE(label)
>
>     def emit_cmp_int(self, op: str, label: int) -> str:
>         frame.pop()
>         mapping = {
>             "==": self.jvm.emitIFICMPEQ,
>             "!=": self.jvm.emitIFICMPNE,
>             "<": self.jvm.emitIFICMPLT,
>             "<=": self.jvm.emitIFICMPLE,
>             ">": self.jvm.emitIFICMPGT,
>             ">=": self.jvm.emitIFICMPGE,
>         }
>         return mapping[op](label)
>     ...
> ```
>
> Hành vi của hàm emit_cmp_int() liệu có sai ở đâu không ạ. Cụ thể là hàm này dùng để sinh nhóm lệnh so sánh if_icmpxx, mà em có tham khảo một vài nguồn thì hiệu ứng stack của nhóm lệnh này là ăn mất 2 phần tử trên cùng của stack nhưng trong khi hàm chỉ gọi frame.pop() 1 lần thôi ạ.
>
> Liệu em có sai sót trong quá trình đọc code base hay tham khảo tài liệu không ạ. Em cảm ơn thầy ạ

> [!success] Admin DuyLMS - 3 ngày trước (1 trả lời)
> Chào em,
>
> Em quan sát đúng.
>
> Các helper khác trong Emitter đều nhận frame để cập nhật operand stack. Ba hàm emit_if_false, emit_if_true, emit_cmp_int đang thiếu tham số frame trong chữ ký dù thân hàm gọi frame.pop() — đây là chỗ chưa nhất quán trong starter.
>
> Về hiệu ứng stack:
>
> ifeq / ifne (dùng trong emit_if_false / emit_if_true): lấy đi 1 phần tử trên cùng của stack.
>
> Nhóm if_icmpxx (dùng trong emit_cmp_int): lấy đi 2 phần tử và không đẩy giá trị mới lên stack.
>
> Do đó với emit_cmp_int, việc chỉ gọi frame.pop() một lần là chưa khớp hiệu ứng stack của lệnh. Khi triển khai CodeGenerator, em cần chỉnh các helper này cho đúng chữ ký và đúng số lần cập nhật stack (cùng quy ước với các hàm emit_* khác), rồi truyền frame khi gọi.
>
> Em cảm ơn.
