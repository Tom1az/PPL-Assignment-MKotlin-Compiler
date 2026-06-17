"""Frame management for MKotlin code generation — Assignment 4 (skeleton).

Tracks the current method's max stack depth, local-variable indices, and label
generation.  Implement as needed.
"""


class Frame:
    def __init__(self, name: str, return_type):
        self.name = name
        self.return_type = return_type
        self.current_label = 0
        self.current_index = 0
        self.max_index = 0
        self.cur_op_stack_size = 0
        self.max_op_stack_size = 0

    def get_new_label(self) -> int:
        label = self.current_label
        self.current_label += 1
        return label

    def get_new_index(self) -> int:
        index = self.current_index
        self.current_index += 1
        self.max_index = max(self.max_index, self.current_index)
        return index

    def push(self, n: int = 1):
        self.cur_op_stack_size += n
        self.max_op_stack_size = max(self.max_op_stack_size, self.cur_op_stack_size)

    def pop(self, n: int = 1):
        self.cur_op_stack_size -= n
