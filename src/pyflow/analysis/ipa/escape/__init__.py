"""IPA escape analysis.

This package provides escape analysis capabilities for Inter-procedural Analysis (IPA),
determining which objects escape function boundaries through returns, parameters,
or global access.

Key components:
- Object escape flags: Track how objects escape (return, parameter, global)
- Escape propagation: Propagate escape information through object relationships
- Context analysis: Analyze escape behavior within function contexts

Escape analysis is crucial for:
- Memory management optimization
- Determining object lifetimes
- Stack vs heap allocation decisions
- Security analysis (information flow)
"""

from . import objectescape
