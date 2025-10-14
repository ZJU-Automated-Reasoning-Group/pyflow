"""IPA calling convention and argument handling.

This package provides the calling convention infrastructure for Inter-procedural
Analysis (IPA), handling function call binding, argument passing, and parameter
matching between callers and callees.

Key components:
- CallBinder: Binds function calls to their implementations
- CPA integration: Uses CPA (Constraint-based Analysis) for type handling
- Transfer functions: Handle argument transfer between contexts
- Parameter matching: Matches actual arguments to formal parameters

The calling module enables precise inter-procedural analysis by properly
modeling how data flows between function calls and returns.
"""

from . import callbinder, cpa, transfer
