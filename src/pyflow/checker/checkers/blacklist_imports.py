# Blacklist checker for imports
import ast

from ..core import blacklist
from ..core import test_properties as test


@test.checks("Import")
@test.with_id("B401-B415")
def check_blacklisted_imports(context):
    """Check for blacklisted module imports"""
    if not isinstance(getattr(context, 'node', None), ast.Import):
        return None
    
    issues = [blacklist.blacklist_manager.check_blacklist("Import", alias.name, context) 
              for alias in context.node.names]
    return [issue for issue in issues if issue] or None


@test.checks("ImportFrom")
@test.with_id("B401-B415")
def check_blacklisted_import_from(context):
    """Check for blacklisted from imports"""
    node = getattr(context, 'node', None)
    if not isinstance(node, ast.ImportFrom) or not node.module:
        return None
    
    return blacklist.blacklist_manager.check_blacklist("ImportFrom", node.module, context)
