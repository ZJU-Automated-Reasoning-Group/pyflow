# Check for hardcoded passwords
import ast
import re

from ..core import issue
from ..core import test_properties as test

RE_WORDS = "(pas+wo?r?d|pass(phrase)?|pwd|token|secrete?)"
RE_CANDIDATES = re.compile(f"(^{RE_WORDS}$|_{RE_WORDS}_|^{RE_WORDS}_|_{RE_WORDS}$)", re.IGNORECASE)


def _report(value):
    """Create a hardcoded password issue"""
    return issue.Issue(
        severity="LOW",
        confidence="MEDIUM",
        cwe=issue.Cwe.HARD_CODED_PASSWORD,
        text=f"Possible hardcoded password: '{value}'",
    )


@test.checks("Str")
@test.with_id("B105")
def hardcoded_password_string(context):
    """Check for hardcoded password strings"""
    node = context.node
    parent = getattr(node, '_bandit_parent', None)
    
    if isinstance(parent, ast.Assign):
        # Look for "candidate='some_string'"
        for targ in parent.targets:
            if isinstance(targ, ast.Name) and RE_CANDIDATES.search(targ.id):
                return _report(node.s)
            elif isinstance(targ, ast.Attribute) and RE_CANDIDATES.search(targ.attr):
                return _report(node.s)

    elif isinstance(parent, (ast.Subscript, ast.Index)) and RE_CANDIDATES.search(node.s):
        # Look for "dict[candidate]='some_string'"
        grandparent = getattr(parent, '_bandit_parent', None)
        if isinstance(grandparent, ast.Assign) and isinstance(grandparent.value, ast.Str):
            return _report(grandparent.value.s)

    elif isinstance(parent, ast.Compare):
        # Look for "candidate == 'some_string'"
        left = parent.left
        if isinstance(left, (ast.Name, ast.Attribute)) and RE_CANDIDATES.search(left.id if isinstance(left, ast.Name) else left.attr):
            if parent.comparators and isinstance(parent.comparators[0], ast.Str):
                return _report(parent.comparators[0].s)


@test.checks("Call")
@test.with_id("B106")
def hardcoded_password_funcarg(context):
    """Check for hardcoded password function arguments"""
    # Look for "function(candidate='some_string')"
    for kw in context.node.keywords:
        if isinstance(kw.value, ast.Str) and RE_CANDIDATES.search(kw.arg):
            return _report(kw.value.s)


@test.checks("FunctionDef")
@test.with_id("B107")
def hardcoded_password_default(context):
    """Check for hardcoded password argument defaults"""
    # Look for "def function(candidate='some_string')"
    defs = [None] * (
        len(context.node.args.args) - len(context.node.args.defaults)
    )
    defs.extend(context.node.args.defaults)

    # Go through all (param, value)s and look for candidates
    for key, val in zip(context.node.args.args, defs):
        if isinstance(key, (ast.Name, ast.arg)):
            # Skip if the default value is None
            if val is None or (
                isinstance(val, (ast.Constant, ast.NameConstant))
                and val.value is None
            ):
                continue
            if isinstance(val, ast.Str) and RE_CANDIDATES.search(key.arg):
                return _report(val.s)
