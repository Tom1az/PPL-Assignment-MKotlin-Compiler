"""Frame management for MKotlin code generation — Assignment 4 (skeleton).

Tracks the current method's max stack depth, local-variable indices, and label
generation.  Implement as needed.
"""


class Frame:
    # ------------------------------------------------------------------ #
    #  ADDED (Assignment 4): the break / continue labels of the loops     #
    #  currently being generated, innermost last.                         #
    #                                                                    #
    #  Declared here as a class-level default rather than in __init__ so  #
    #  that no existing line of this class has to change.  It is an       #
    #  immutable tuple and ``enter_loop`` / ``exit_loop`` rebind it, so    #
    #  every Frame still gets its own value and the shared default is     #
    #  never mutated.                                                     #
    # ------------------------------------------------------------------ #
    loop_labels: tuple = ()

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

    # ==================================================================== #
    #  ADDED (Assignment 4) — loop jump targets.  Everything above this    #
    #  line is the original skeleton, unchanged.                           #
    #                                                                      #
    #  ``while`` / ``for`` call enter_loop before generating the body and   #
    #  exit_loop afterwards; ``break`` / ``continue`` read the labels of    #
    #  the innermost loop back, so nested loops each jump to their own.     #
    # ==================================================================== #
    def enter_loop(self):
        """Reserve the break and continue labels of the loop being generated."""
        self.loop_labels = self.loop_labels + (
            (self.get_new_label(), self.get_new_label()),
        )

    def exit_loop(self):
        """Release the innermost loop's labels once its body is generated."""
        self.loop_labels = self.loop_labels[:-1]

    def get_break_label(self) -> int:
        """The label ``break`` jumps to: the first block after the loop."""
        return self.loop_labels[-1][0]

    def get_continue_label(self) -> int:
        """The label ``continue`` jumps to: the loop's update / re-test block."""
        return self.loop_labels[-1][1]

    def merge_alternative(self, depth: int):
        """Rewind the current depth to ``depth`` after one exclusive path.

        The paths of an ``if`` / ``when`` expression and of ``&&`` / ``||`` are
        alternatives: only one of them ever runs, so their pushes must not be
        summed into ``max_op_stack_size``.  Each path is generated starting from
        the same ``depth``, and this puts the frame back so the next one is too.
        """
        self.pop(self.cur_op_stack_size - depth)
