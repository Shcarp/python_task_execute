import ctypes

class AtomicOperations:
    @staticmethod
    def atomic_add(value, increment):
        asm_code = """
        add {0}, {0}, {1}
        """

        asm_code = asm_code.format(value, increment)

        asm_func = ctypes.CFUNCTYPE(None)(ctypes.addressof(ctypes.c_int.from_address(0).value))
        asm_func._code = asm_code
        asm_func()

    @staticmethod
    def atomic_sub(value, decrement):
        asm_code = """
        sub {0}, {0}, {1}
        """

        asm_code = asm_code.format(value, decrement)

        asm_func = ctypes.CFUNCTYPE(None)(ctypes.addressof(ctypes.c_int.from_address(0).value))
        asm_func._code = asm_code
        asm_func()
