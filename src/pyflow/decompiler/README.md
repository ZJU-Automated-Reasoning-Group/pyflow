# NOTE

This dir (`pyflow/decompiler`) is not used for now.
It has been updated to be compatible with Python 3.

## Python 3 Compatibility Updates

The decompiler was originally designed for Python 2, but has been updated
to work with Python 3 with the following changes:

### Function Attribute Access
- `func.func_code` → `func.__code__`
- `func.func_defaults` → `func.__defaults__`
- `func.func_globals` → `func.__globals__`

### Opcode Changes
Many opcodes were removed or changed in Python 3. The following opcodes
no longer exist and have been handled appropriately:

- `SETUP_LOOP` - removed (loops use SETUP_FINALLY for exception handling)
- `BREAK_LOOP` - removed (break statements handled differently)
- `SETUP_EXCEPT` - removed (exception handling uses SETUP_FINALLY)
- `END_FINALLY` - removed (handled by SETUP_FINALLY cleanup)
- `ROT_TWO`, `ROT_THREE`, `ROT_FOUR` - removed (stack rotation changes)
- `DUP_TOP`, `DUP_TOPX` - removed (duplication opcodes changed)

### Stack Operations
Stack manipulation opcodes were simplified to only include `POP_TOP`
since other stack operations work differently in Python 3.

All other Python 2/3 compatibility issues have been addressed.
