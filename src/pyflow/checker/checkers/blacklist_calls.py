# Blacklist checker for function calls
# Based on blacklist system
import ast

from ..core import blacklist
from ..core import test_properties as test


@test.checks("Call")
@test.test_id("B301-B323")
def check_blacklisted_calls(context):
    """Check for blacklisted function calls"""
    qualname = getattr(context, 'call_function_name_qual', None)
    return blacklist.blacklist_manager.check_blacklist("Call", qualname, context) if qualname else None
