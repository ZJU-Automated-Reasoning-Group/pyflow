"""IPA constraint system.

This package provides the constraint system used by Inter-procedural Analysis (IPA)
to model data flow, function calls, and object relationships across function boundaries.

Key components:
- Base constraints: Fundamental constraint types (copy, load, store, split)
- Call constraints: Function call and return modeling
- Flow constraints: Control and data flow relationships
- Node constraints: Object and slot relationship modeling
- Qualifiers: Type qualifiers for constraint propagation
- Split constraints: Complex data flow splitting

The constraint system enables precise inter-procedural analysis by modeling
how data flows between function calls and returns while maintaining context sensitivity.
"""

from . import base, calls, flow, node, qualifiers, split
